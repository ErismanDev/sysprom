from django import forms
from .models import ConcessaoMedalha, Medalha, PUBLICO_ALVO_CHOICES, ModeloNota, BemMovel, TombamentoBemMovel, ProdutoAlmoxarifado, EntradaAlmoxarifado, SaidaAlmoxarifado, EquipamentoOperacional, TempoUsoEquipamento, TransferenciaEquipamento
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from .models import Militar, FichaConceitoOficiais, FichaConceitoPracas, Documento, ComissaoPromocao, MembroComissao, SessaoComissao, DeliberacaoComissao, DocumentoSessao, AtaSessao, ModeloAta, CargoComissao, QuadroAcesso, QuadroFixacaoVagas, FuncaoMilitar, Promocao, Qualificacao, Lotacao, MilitarFuncao, Orgao, GrandeComando, Unidade, SubUnidade, Elogio, Punicao, TIPO_FUNCAO_CHOICES, STATUS_LOTACAO_CHOICES, UsuarioFuncaoMilitar, TituloPublicacaoConfig, Publicacao, Afastamento, DocumentoAfastamento, PlanoFerias, Ferias, DocumentoFerias, Viatura, Averbacao, Arma, ArmaParticular, MovimentacaoArma, ConfiguracaoArma, ConfiguracaoMunicao, CautelaArma, CautelaArmaColetiva, Municao, EntradaMunicao, SaidaMunicao, DevolucaoMunicao, CautelaMunicao, ProcessoAdministrativo, LicencaEspecial
# from django_ckeditor_5.widgets import CKEditor5Widget  # Temporariamente comentado


def verificar_choque_datas_afastamentos(militar, data_inicio, data_fim, instance=None):
    """
    Verifica se há choque de datas entre o período informado e outros afastamentos do militar.
    
    Args:
        militar: Instância do Militar
        data_inicio: Data de início do período
        data_fim: Data de fim do período (pode ser None)
        instance: Instância atual sendo editada (para excluir da verificação)
    
    Returns:
        Lista de mensagens de erro descrevendo os choques encontrados
    """
    if not militar or not data_inicio:
        return []
    
    erros = []
    
    # Se não há data_fim, considerar apenas a data_inicio como período de 1 dia
    if not data_fim:
        data_fim = data_inicio
    
    # Verificar choques com Afastamentos
    afastamentos = Afastamento.objects.filter(militar=militar)
    if instance and hasattr(instance, 'pk') and instance.pk:
        # Se está editando um Afastamento, excluir ele mesmo da verificação
        if isinstance(instance, Afastamento):
            afastamentos = afastamentos.exclude(pk=instance.pk)
    
    for afastamento in afastamentos:
        # Ignorar afastamentos cancelados ou encerrados
        if afastamento.status in ['CANCELADO', 'ENCERRADO']:
            continue
        
        # Determinar data_fim do afastamento existente
        afastamento_fim = afastamento.data_fim_real or afastamento.data_fim_prevista
        
        # Verificar sobreposição de períodos
        # Dois períodos se sobrepõem se: inicio1 <= fim2 AND fim1 >= inicio2
        # Se não tem data_fim, considerar como período indefinido (qualquer data futura choca)
        if afastamento_fim:
            # Tem data de fim definida
            if data_inicio <= afastamento_fim and data_fim >= afastamento.data_inicio:
                tipo_display = afastamento.get_tipo_afastamento_display()
                erros.append(
                    f"Afastamento ({tipo_display}) de {afastamento.data_inicio.strftime('%d/%m/%Y')} "
                    f"a {afastamento_fim.strftime('%d/%m/%Y')}"
                )
        else:
            # Não tem data de fim - está ativo indefinidamente
            # Qualquer período que comece após o início do afastamento vai choque
            if data_inicio >= afastamento.data_inicio:
                tipo_display = afastamento.get_tipo_afastamento_display()
                erros.append(
                    f"Afastamento ({tipo_display}) de {afastamento.data_inicio.strftime('%d/%m/%Y')} "
                    f"(sem data de fim prevista)"
                )
    
    # Verificar choques com Férias
    ferias = Ferias.objects.filter(militar=militar)
    if instance and hasattr(instance, 'pk') and instance.pk:
        # Se está editando uma Ferias, excluir ela mesma da verificação
        if isinstance(instance, Ferias):
            ferias = ferias.exclude(pk=instance.pk)
    
    for ferias_item in ferias:
        # Ignorar férias canceladas ou reprogramadas
        if ferias_item.status in ['CANCELADA', 'REPROGRAMADA']:
            continue
        
        # Verificar sobreposição de períodos
        if data_inicio <= ferias_item.data_fim and data_fim >= ferias_item.data_inicio:
            tipo_display = ferias_item.get_tipo_display()
            erros.append(
                f"Férias ({tipo_display}) de {ferias_item.data_inicio.strftime('%d/%m/%Y')} "
                f"a {ferias_item.data_fim.strftime('%d/%m/%Y')}"
            )
    
    # Verificar choques com Licenças Especiais
    licencas = LicencaEspecial.objects.filter(militar=militar)
    if instance and hasattr(instance, 'pk') and instance.pk:
        # Se está editando uma LicencaEspecial, excluir ela mesma da verificação
        if isinstance(instance, LicencaEspecial):
            licencas = licencas.exclude(pk=instance.pk)
    
    for licenca in licencas:
        # Ignorar licenças canceladas
        if licenca.status == 'CANCELADA':
            continue
        
        # Verificar se tem data_fim
        if not licenca.data_fim:
            continue
        
        # Verificar sobreposição de períodos
        if data_inicio <= licenca.data_fim and data_fim >= licenca.data_inicio:
            erros.append(
                f"Licença Especial ({licenca.decenio}º decênio) de {licenca.data_inicio.strftime('%d/%m/%Y')} "
                f"a {licenca.data_fim.strftime('%d/%m/%Y')}"
            )
    
    return erros


class MilitarForm(forms.ModelForm):
    class Meta:
        model = Militar
        fields = [
            'numeracao_antiguidade', 'matricula', 'nome_completo', 'nome_guerra', 'cpf', 'rg', 'rgbm', 'orgao_expedidor',
            'data_nascimento', 'sexo', 'etnia', 'grupo_sanguineo', 'fator_rh', 'nome_pai', 'nome_mae', 
            'nacionalidade', 'naturalidade', 'uf_naturalidade', 'titulo_eleitor', 'zona_eleitoral', 'secao_eleitoral', 'cnh_numero', 'cnh_categoria', 
            'cnh_validade', 'banco_codigo', 'banco_nome', 'agencia', 'conta', 'pis_pasep', 'gratificacao', 'altura', 'peso',
            'combat_shirt', 'camisa', 'calca', 'comprimento_calca', 'gorro', 'coturno',
            'quadro', 'posto_graduacao', 'data_ingresso', 'data_promocao_atual', 'situacao', 'classificacao', 'comportamento', 'email', 'telefone',
            'celular', 'endereco', 'cidade', 'uf', 'cep', 'foto', 'observacoes',
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
            'rgbm': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da Identidade Militar (RGBM)'
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
            'etnia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'grupo_sanguineo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fator_rh': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nome_pai': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do pai'
            }),
            'nome_mae': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo da mãe'
            }),
            'nacionalidade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'naturalidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade de nascimento'
            }),
            'uf_naturalidade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'titulo_eleitor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do título de eleitor'
            }),
            'zona_eleitoral': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 123'
            }),
            'secao_eleitoral': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 456'
            }),
            'cnh_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da CNH'
            }),
            'cnh_categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cnh_validade': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'banco_codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código do banco'
            }),
            'banco_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do banco'
            }),
            'agencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da agência'
            }),
            'conta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da conta'
            }),
            'pis_pasep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do PIS/PASEP'
            }),
            'altura': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Altura em cm',
                'step': '0.01',
                'min': '0'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Peso em kg',
                'step': '0.01',
                'min': '0'
            }),
            'combat_shirt': forms.Select(attrs={
                'class': 'form-select'
            }),
            'camisa': forms.Select(attrs={
                'class': 'form-select'
            }),
            'calca': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comprimento_calca': forms.Select(attrs={
                'class': 'form-select'
            }),
            'gorro': forms.Select(attrs={
                'class': 'form-select'
            }),
            'coturno': forms.Select(attrs={
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
            'classificacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comportamento': forms.Select(attrs={
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
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Logradouro, número, complemento, bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da cidade'
            }),
            'uf': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control cep-mask',
                'placeholder': '00000-000'
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
    tempo_posto_anos = forms.IntegerField(
        label="Anos no Posto",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'placeholder': '0'
        })
    )
    tempo_posto_meses = forms.IntegerField(
        label="Meses no Posto",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '11',
            'placeholder': '0'
        })
    )
    tempo_posto_dias = forms.IntegerField(
        label="Dias no Posto",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '30',
            'placeholder': '0'
        })
    )
    tempo_posto_extenso = forms.CharField(
        label="Tempo no Posto (por extenso)",
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',
            'style': 'background-color: #f8f9fa;'
        })
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
            tempo_detalhado = militar.tempo_posto_atual_detalhado()
            
            # Preencher campos de anos, meses e dias
            self.fields['tempo_posto_anos'].initial = tempo_detalhado.years
            self.fields['tempo_posto_meses'].initial = tempo_detalhado.months
            self.fields['tempo_posto_dias'].initial = tempo_detalhado.days
            
            # Preencher campo por extenso
            if self.instance:
                self.fields['tempo_posto_extenso'].initial = self.instance.tempo_posto_extenso
            else:
                # Criar instância temporária para calcular o extenso
                temp_instance = self.Meta.model()
                temp_instance.tempo_posto_anos = tempo_detalhado.years
                temp_instance.tempo_posto_meses = tempo_detalhado.months
                temp_instance.tempo_posto_dias = tempo_detalhado.days
                self.fields['tempo_posto_extenso'].initial = temp_instance.tempo_posto_extenso

class FichaConceitoPracasForm(forms.ModelForm):
    tempo_posto_anos = forms.IntegerField(
        label="Anos no Posto",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'placeholder': '0'
        })
    )
    tempo_posto_meses = forms.IntegerField(
        label="Meses no Posto",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '11',
            'placeholder': '0'
        })
    )
    tempo_posto_dias = forms.IntegerField(
        label="Dias no Posto",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '30',
            'placeholder': '0'
        })
    )
    tempo_posto_extenso = forms.CharField(
        label="Tempo no Posto (por extenso)",
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',
            'style': 'background-color: #f8f9fa;'
        })
    )
    class Meta:
        model = FichaConceitoPracas
        exclude = ['militar', 'pontos']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Observações...'}),
            # Campos de punições
            'punicao_repreensao': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'punicao_detencao': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'punicao_prisao': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'falta_aproveitamento': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            # Campos de cursos
            'cursos_especializacao': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'cursos_cfsd': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'cursos_chc': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'cursos_chsgt': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'cursos_cas': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'cursos_cho': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'cursos_civis_tecnico': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'cursos_civis_superior': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'cursos_civis_especializacao': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'cursos_civis_mestrado': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'cursos_civis_doutorado': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            # Medalhas
            'medalha_federal': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'medalha_estadual': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'medalha_cbmepi': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            # Elogios
            'elogio_individual': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'elogio_coletivo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        militar = kwargs.pop('militar', None)
        super().__init__(*args, **kwargs)
        
        if militar:
            tempo_detalhado = militar.tempo_posto_atual_detalhado()
            
            # Preencher campos de anos, meses e dias
            self.fields['tempo_posto_anos'].initial = tempo_detalhado.years
            self.fields['tempo_posto_meses'].initial = tempo_detalhado.months
            self.fields['tempo_posto_dias'].initial = tempo_detalhado.days
            
            # Preencher campo por extenso
            if self.instance:
                self.fields['tempo_posto_extenso'].initial = self.instance.tempo_posto_extenso
            else:
                # Criar instância temporária para calcular o extenso
                temp_instance = self.Meta.model()
                temp_instance.tempo_posto_anos = tempo_detalhado.years
                temp_instance.tempo_posto_meses = tempo_detalhado.months
                temp_instance.tempo_posto_dias = tempo_detalhado.days
                self.fields['tempo_posto_extenso'].initial = temp_instance.tempo_posto_extenso


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
    
    # Campo militar customizado para aceitar IDs
    militar = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'id_militar'}),
        required=True,
        label='Militar',
        help_text='Digite o nome do militar que possui função do grupo de comissões'
    )
    
    class Meta:
        model = MembroComissao
        fields = ['comissao', 'militar', 'data_nomeacao', 'data_termino', 'ativo', 'observacoes']
        widgets = {
            'comissao': forms.HiddenInput(),
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
    
    def clean_militar(self):
        militar_value = self.cleaned_data.get('militar')
        
        if not militar_value:
            raise forms.ValidationError('Selecione um militar.')
        
        try:
            # Se é um ID numérico (string ou int)
            if isinstance(militar_value, str):
                militar_id = int(militar_value)
            else:
                militar_id = militar_value
            
            militar = Militar.objects.get(id=militar_id)
            return militar
        except (Militar.DoesNotExist, ValueError, TypeError):
            raise forms.ValidationError('Militar não encontrado.')
    
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
        # REMOVIDA A VALIDAÇÃO QUE IMPEDIA HORÁRIOS QUE PASSAM DA MEIA-NOITE
        # O sistema já está preparado para lidar com escalas que começam em um dia e terminam no dia seguinte
        # Exemplo: 22:00 até 02:00 (turno noturno)
        
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
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
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
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
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
    funcao_militar = forms.ModelChoiceField(
        queryset=FuncaoMilitar.objects.all().order_by('nome'),
        required=True,
        label='Função/Cargo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'is_active', 'is_staff', 'is_superuser', 'funcao_militar'
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

class SelecaoFuncaoLotacaoForm(forms.Form):
    """Formulário para seleção de função militar e lotação no login"""
    
    funcao_militar_usuario = forms.ModelChoiceField(
        queryset=UsuarioFuncaoMilitar.objects.none(),
        empty_label="Selecione uma função",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_funcao_militar_usuario',
            'required': True
        }),
        label="Função Militar"
    )
    
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar queryset com todas as funções do usuário (ativas e inativas)
        if self.user:
            self.fields['funcao_militar_usuario'].queryset = UsuarioFuncaoMilitar.objects.filter(
                usuario=self.user
            ).select_related('funcao_militar', 'orgao', 'grande_comando', 'unidade', 'sub_unidade').order_by(
                'funcao_militar__ordem', 'funcao_militar__nome'
            )
    
    def clean(self):
        cleaned_data = super().clean()
        funcao_militar_usuario = cleaned_data.get('funcao_militar_usuario')
        
        # Validar se uma função foi selecionada
        if not funcao_militar_usuario:
            raise forms.ValidationError("Selecione uma função militar.")
        
        # Verificar se a função pertence ao usuário
        if self.user and funcao_militar_usuario.usuario != self.user:
            raise forms.ValidationError("Você não tem permissão para usar esta função.")
        
        return cleaned_data


class FuncaoMilitarForm(forms.ModelForm):
    """Formulário para Função Militar - Sistema Antigo (apenas campos básicos)"""
    
    class Meta:
        model = FuncaoMilitar
        fields = [
            'nome', 'acesso_sigilo', 'ordem', 'acesso', 'nivel', 
            'grupo', 'publicacao', 'tipo_comissao', 'descricao', 'ativo'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da função militar'
            }),
            'acesso_sigilo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ordem': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'acesso': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nivel': forms.Select(attrs={
                'class': 'form-select'
            }),
            'grupo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'publicacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_comissao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição da função militar (opcional)'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS para melhorar a aparência
        for field_name, field in self.fields.items():
            if field_name != 'ativo':
                field.widget.attrs.update({'class': field.widget.attrs.get('class', '') + ' form-control'})
        
        # Tornar campos obrigatórios
        self.fields['nome'].required = True
        self.fields['acesso_sigilo'].required = True
        self.fields['acesso'].required = True
        self.fields['nivel'].required = True
        self.fields['grupo'].required = True
        self.fields['publicacao'].required = True
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if nome:
            nome = nome.strip()
            if len(nome) < 3:
                raise forms.ValidationError('O nome da função deve ter pelo menos 3 caracteres.')
            if len(nome) > 200:
                raise forms.ValidationError('O nome da função deve ter no máximo 200 caracteres.')
        return nome
    
    def clean_ordem(self):
        ordem = self.cleaned_data.get('ordem')
        if ordem is not None and ordem < 0:
            raise forms.ValidationError('A ordem deve ser um número positivo ou zero.')
        return ordem
    
    def clean_descricao(self):
        descricao = self.cleaned_data.get('descricao')
        if descricao and len(descricao) > 1000:
            raise forms.ValidationError('A descrição deve ter no máximo 1000 caracteres.')
        return descricao
    
    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        
        # Verificar se já existe uma função com o mesmo nome (exceto na edição)
        if nome and self.instance.pk is None:  # Nova função
            if FuncaoMilitar.objects.filter(nome__iexact=nome).exists():
                raise forms.ValidationError('Já existe uma função militar com este nome.')
        elif nome and self.instance.pk:  # Edição
            if FuncaoMilitar.objects.filter(nome__iexact=nome).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Já existe uma função militar com este nome.')
        
        return cleaned_data



class PromocaoForm(forms.ModelForm):
    """Formulário para criação e edição de promoções"""
    
    class Meta:
        model = Promocao
        fields = [
            'militar', 'posto_anterior', 'posto_novo', 'criterio',
            'data_promocao', 'data_publicacao', 'numero_ato', 'observacoes', 'is_historica'
        ]
        widgets = {
            'militar': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'posto_anterior': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'posto_novo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'criterio': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'data_promocao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'data_publicacao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'numero_ato': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PORTARIA Nº 123/2024',
                'maxlength': '200'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Observações complementares (opcional)'
            }),
            'is_historica': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_is_historica'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas militares ativos (excluir inativos, transferidos, aposentados, exonerados)
        from .models import Militar
        militares_ativos = Militar.objects.filter(
            classificacao='ATIVO'
        ).order_by('nome_completo')
        
        # Se está editando, incluir o militar atual mesmo que esteja inativo
        if self.instance and self.instance.pk and self.instance.militar:
            militar_atual = self.instance.militar
            if militar_atual.classificacao != 'ATIVO':
                # Adicionar o militar atual ao queryset mesmo que esteja inativo
                militares_ids = list(militares_ativos.values_list('id', flat=True))
                militares_ids.append(militar_atual.id)
                militares_ativos = Militar.objects.filter(id__in=militares_ids).order_by('nome_completo')
        
        self.fields['militar'].queryset = militares_ativos
    
    def clean_numero_ato(self):
        """Valida o número do ato"""
        numero_ato = self.cleaned_data.get('numero_ato')
        if numero_ato and len(numero_ato) > 200:
            raise forms.ValidationError(
                'O número do ato não pode exceder 200 caracteres.'
            )
        return numero_ato
    
    def clean(self):
        """Validações gerais do formulário"""
        cleaned_data = super().clean()
        data_promocao = cleaned_data.get('data_promocao')
        data_publicacao = cleaned_data.get('data_publicacao')
        
        if data_promocao and data_publicacao:
            if data_publicacao < data_promocao:
                raise forms.ValidationError(
                    'A data de publicação não pode ser anterior à data da promoção.'
                )
        
        return cleaned_data 


# ==========================
# Formulários - Medalhas
# ==========================

UF_CHOICES = [
    ('', 'Selecione o Estado'),
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
]

class ConcessaoMedalhaMilitarForm(forms.ModelForm):
    medalha_nome = forms.CharField(required=False, label='Medalha (digite o nome)', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Medalha Mérito Bombeiro'}))
    class Meta:
        model = ConcessaoMedalha
        fields = ['medalha', 'militar', 'orgao_externo', 'data_concessao', 'documento_tipo', 'portaria_numero', 'portaria_data', 'indicado_por_nome', 'indicado_por_funcao', 'observacoes']
        widgets = {
            'medalha': forms.Select(attrs={'class': 'form-select'}),
            'militar': forms.Select(attrs={'class': 'form-select'}),
            'orgao_externo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Órgão/Instituição (se externa)'}),
            'data_concessao': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'documento_tipo': forms.Select(attrs={'class': 'form-select'}),
            'portaria_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'portaria_data': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'indicado_por_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de quem indicou'}),
            'indicado_por_funcao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Função de quem indicou'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Permitir todas no seletor; mas se vier nome digitado, vamos criar/usar no clean
        self.fields['medalha'].queryset = Medalha.objects.filter(ativo=True)
        # Permitir digitar o nome da medalha em vez de obrigar seleção
        self.fields['medalha'].required = False
        self.fields['militar'].required = True
        # Campo de órgão externo não é necessário para Tempo de Serviço
        self.fields['orgao_externo'].required = False
        # Documento pode ficar em branco na proposta
        self.fields['documento_tipo'].required = False
        self.fields['portaria_numero'].required = False
        self.fields['portaria_data'].required = False
        medalha_id_inicial = self.initial.get('medalha') or (self.instance.medalha_id if getattr(self.instance, 'medalha_id', None) else None)
        if medalha_id_inicial:
            try:
                med_tipo = Medalha.objects.only('tipo').get(pk=medalha_id_inicial).tipo
                if med_tipo == 'TEMPO_SERVICO':
                    from django import forms as dj_forms
                    self.fields['orgao_externo'].widget = dj_forms.HiddenInput()
            except Medalha.DoesNotExist:
                pass

    def clean(self):
        cleaned = super().clean()
        medalha = cleaned.get('medalha')
        medalha_nome = cleaned.get('medalha_nome')
        militar = cleaned.get('militar')
        if medalha and militar:
            if ConcessaoMedalha.objects.filter(militar=militar, medalha=medalha).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este militar já foi agraciado com esta medalha.')
        # Se não selecionou da lista e digitou um nome, criar/usar medalha de HONRA
        if not medalha and medalha_nome:
            codigo = medalha_nome.upper().strip().replace(' ', '_')[:30]
            obj, _ = Medalha.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nome': medalha_nome.strip(),
                    'tipo': 'HONRA',
                    'grau_tempo_servico': None,
                    'publico_alvo_padrao': 'BOMBEIRO_MILITAR',
                    'ativo': True,
                },
            )
            cleaned['medalha'] = obj
            self.instance.medalha = obj
            medalha = obj
        # Em edição: se o campo medalha não vier no POST, manter a existente
        if not medalha and getattr(self.instance, 'pk', None):
            cleaned['medalha'] = self.instance.medalha
        # Para medalhas de Tempo de Serviço, ignorar/limpar órgão externo (é interna corporis)
        if medalha and getattr(medalha, 'tipo', None) == 'TEMPO_SERVICO':
            cleaned['orgao_externo'] = ''
            self.instance.orgao_externo = ''
        return cleaned


class ConcessaoMedalhaExternoForm(forms.ModelForm):
    categoria_externa = forms.ChoiceField(
        choices=[(c, n) for c, n in PUBLICO_ALVO_CHOICES if c != 'BOMBEIRO_MILITAR'],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    uf_externa = forms.ChoiceField(
        choices=UF_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = ConcessaoMedalha
        fields = ['medalha', 'categoria_externa', 'forca_externa', 'uf_externa', 'posto_graduacao_externo', 'funcao_externa', 'nome_externo', 'documento_externo', 'orgao_externo', 'data_concessao', 'documento_tipo', 'portaria_numero', 'portaria_data', 'indicado_por_nome', 'indicado_por_funcao', 'observacoes']
        widgets = {
            'medalha': forms.Select(attrs={'class': 'form-select'}),
            'forca_externa': forms.Select(attrs={'class': 'form-select'}),
            # uf_externa usa ChoiceField acima para mostrar Estados por extenso
            'posto_graduacao_externo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Posto/Graduação'}),
            'funcao_externa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo, Função ou Número (ex: Sargento, 123, etc)'}),
            'nome_externo': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_externo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF (somente números)'}),
            'orgao_externo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_concessao': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'documento_tipo': forms.Select(attrs={'class': 'form-select'}),
            'portaria_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'portaria_data': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'indicado_por_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de quem indicou'}),
            'indicado_por_funcao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Função de quem indicou'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medalha'].queryset = Medalha.objects.filter(ativo=True)
        # Documento pode ficar em branco na proposta
        self.fields['documento_tipo'].required = False
        self.fields['portaria_numero'].required = False
        self.fields['portaria_data'].required = False
        # Placeholders e obrigatoriedades dinâmicas serão tratados via JS no template


class DateInput(forms.DateInput):
    input_type = 'date'
    
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({'class': 'form-control'})
        super().__init__(attrs=attrs)
    
    def format_value(self, value):
        """Formatar valor para o formato ISO (YYYY-MM-DD) para campos type='date'"""
        if value is None:
            return ''
        if hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')
        return str(value)

class QualificacaoForm(forms.ModelForm):
    class Meta:
        model = Qualificacao
        fields = [
            'tipo', 'nome_curso', 'carga_horaria', 'instituicao', 
            'data_inicio', 'data_conclusao', 'status_verificacao', 
            'observacoes', 'arquivo_certificado'
        ]
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nome_curso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do curso ou certificação'
            }),
            'carga_horaria': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Carga horária em horas',
                'min': '1'
            }),
            'instituicao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da instituição'
            }),
            'data_inicio': DateInput(),
            'data_conclusao': DateInput(),
            'status_verificacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Observações adicionais'
            }),
            'arquivo_certificado': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar campos opcionais
        self.fields['carga_horaria'].required = False
        self.fields['instituicao'].required = False
        self.fields['data_inicio'].required = False
        self.fields['data_conclusao'].required = False
        self.fields['observacoes'].required = False
        self.fields['arquivo_certificado'].required = False
        
        # Configurar formato de data para os campos de data
        self.fields['data_inicio'].input_formats = ['%Y-%m-%d']
        self.fields['data_conclusao'].input_formats = ['%Y-%m-%d']
        
        # Garantir que as datas sejam carregadas corretamente quando editando
        if self.instance and self.instance.pk:
            if self.instance.data_inicio:
                # Definir o valor inicial diretamente no campo
                self.fields['data_inicio'].initial = self.instance.data_inicio
            if self.instance.data_conclusao:
                # Definir o valor inicial diretamente no campo
                self.fields['data_conclusao'].initial = self.instance.data_conclusao
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_conclusao = cleaned_data.get('data_conclusao')
        
        # Validar se data de conclusão não é anterior à data de início
        if data_inicio and data_conclusao and data_conclusao < data_inicio:
            raise forms.ValidationError('A data de conclusão não pode ser anterior à data de início.')
        
        return cleaned_data


class LotacaoForm(forms.ModelForm):
    """Formulário para gerenciar lotações dos militares"""
    
    class Meta:
        model = Lotacao
        fields = [
            'militar', 'lotacao', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'status', 'data_inicio', 'data_fim', 'observacoes', 'ativo'
        ]
        widgets = {
            'militar': forms.Select(attrs={
                'class': 'form-select militar-autocomplete',
                'data-placeholder': 'Digite o nome do militar...',
                'data-url': '/militares/busca-militares/',
                'data-minimum-input-length': '2'
            }),
            'lotacao': forms.HiddenInput(),
            'orgao': forms.HiddenInput(),
            'grande_comando': forms.HiddenInput(),
            'unidade': forms.HiddenInput(),
            'sub_unidade': forms.HiddenInput(),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a lotação...'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tornar o campo militar obrigatório apenas na criação
        if not self.instance.pk:
            self.fields['militar'].required = True
        else:
            self.fields['militar'].required = False
            self.fields['militar'].widget.attrs['readonly'] = True
        
        # Configurar querysets dos campos do organograma
        from .models import Orgao, GrandeComando, Unidade, SubUnidade
        
        self.fields['orgao'].queryset = Orgao.objects.filter(ativo=True).order_by('sigla')
        self.fields['grande_comando'].queryset = GrandeComando.objects.filter(ativo=True).order_by('sigla')
        self.fields['unidade'].queryset = Unidade.objects.filter(ativo=True).order_by('sigla')
        self.fields['sub_unidade'].queryset = SubUnidade.objects.filter(ativo=True).order_by('sigla')
        
        # Adicionar opção vazia para todos os campos do organograma
        for field_name in ['orgao', 'grande_comando', 'unidade', 'sub_unidade']:
            self.fields[field_name].empty_label = "Selecione..."
            self.fields[field_name].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        status = cleaned_data.get('status')
        
        # Validar se data de fim é posterior à data de início
        if data_inicio and data_fim and data_fim < data_inicio:
            raise forms.ValidationError('A data de fim deve ser posterior à data de início.')
        
        # Se é lotação atual, não deve ter data de fim
        if status == 'ATUAL' and data_fim:
            raise forms.ValidationError('Lotações atuais não devem ter data de fim.')
        
        return cleaned_data


class MilitarFuncaoFormAdmin(forms.ModelForm):
    """Formulário para gerenciar funções dos militares (Admin)"""
    
    class Meta:
        model = MilitarFuncao
        fields = [
            'militar', 'funcao_militar', 'tipo_funcao', 'data_inicio', 'data_fim', 'observacoes', 'ativo'
        ]
        widgets = {
            'militar': forms.Select(attrs={
                'class': 'form-select militar-autocomplete',
                'data-placeholder': 'Digite o nome do militar...',
                'data-url': '/militares/busca-militares/',
                'data-minimum-input-length': '2'
            }),
            'funcao_militar': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_funcao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a função...'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para funções militares
        # Se o usuário tem função do grupo COMISSAO, permitir funções inativas
        from .models import UsuarioFuncaoMilitar
        
        # Obter usuário do contexto ou da instância
        usuario = kwargs.get('user')
        if not usuario and hasattr(self, 'instance') and self.instance:
            # Se for MilitarFuncao, obter usuário através do militar
            if hasattr(self.instance, 'militar') and self.instance.militar:
                usuario = getattr(self.instance.militar, 'user', None)
            # Se for UsuarioFuncaoMilitar, obter usuário diretamente
            elif hasattr(self.instance, 'usuario'):
                usuario = self.instance.usuario
        
        if usuario and UsuarioFuncaoMilitar.objects.filter(
            usuario=usuario, 
            ativo=True, 
            funcao_militar__grupo='COMISSAO'
        ).exists():
            # Usuário com função de comissão pode ver todas as funções (incluindo inativas)
            self.fields['funcao_militar'].queryset = FuncaoMilitar.objects.all().order_by('ordem', 'nome')
        else:
            # Usuário comum só vê funções ativas
            self.fields['funcao_militar'].queryset = FuncaoMilitar.objects.filter(ativo=True).order_by('ordem', 'nome')
        
        self.fields['funcao_militar'].empty_label = "Selecione uma função militar..."
        
        # Tornar o campo militar obrigatório apenas na criação
        if not self.instance.pk:
            self.fields['militar'].required = True
        else:
            self.fields['militar'].required = False
            self.fields['militar'].widget.attrs['readonly'] = True
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        # Validar se data de fim é posterior à data de início
        if data_inicio and data_fim and data_fim < data_inicio:
            raise forms.ValidationError('A data de fim deve ser posterior à data de início.')
        
        return cleaned_data


def get_organizacoes_hierarquicas():
    """Retorna lista hierárquica de organizações para filtro"""
    from .models import Orgao, GrandeComando, Unidade, SubUnidade
    
    choices = [('', 'Todas as organizações')]
    
    # Órgãos
    orgaos = Orgao.objects.filter(ativo=True).order_by('nome')
    for orgao in orgaos:
        choices.append((f'orgao_{orgao.id}', f'🏛️ {orgao.nome}'))
        
        # Grandes Comandos do órgão
        grandes_comandos = GrandeComando.objects.filter(orgao=orgao, ativo=True).order_by('nome')
        for gc in grandes_comandos:
            choices.append((f'gc_{gc.id}', f'  🏢 {gc.nome}'))
            
            # Unidades do grande comando
            unidades = Unidade.objects.filter(grande_comando=gc, ativo=True).order_by('nome')
            for unidade in unidades:
                choices.append((f'unidade_{unidade.id}', f'    🏬 {unidade.nome}'))
                
                # Sub-unidades da unidade
                sub_unidades = SubUnidade.objects.filter(unidade=unidade, ativo=True).order_by('nome')
                for sub_unidade in sub_unidades:
                    choices.append((f'sub_{sub_unidade.id}', f'      🏪 {sub_unidade.nome}'))
    
    return choices


class LotacaoFilterForm(forms.Form):
    """Formulário para filtrar lotações"""
    militar = forms.ModelChoiceField(
        queryset=Militar.objects.filter(classificacao='ATIVO').order_by('nome_guerra'),
        required=False,
        empty_label="Todos os militares",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    organizacao = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organizacao'].choices = get_organizacoes_hierarquicas()
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + STATUS_LOTACAO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class OrgaoForm(forms.ModelForm):
    """Formulário para gerenciar órgãos"""
    
    class Meta:
        model = Orgao
        fields = ['nome', 'sigla', 'ordem', 'descricao', 'endereco', 'cidade', 'latitude', 'longitude', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome completo do órgão...',
                'maxlength': '200'
            }),
            'sigla': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: CBM, PM, PC, etc...',
                'maxlength': '20',
                'style': 'text-transform: uppercase;'
            }),
            'ordem': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ordem de exibição...',
                'min': '1'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição opcional do órgão...'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Endereço completo do órgão...'
            }),
            'cidade': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Selecione a cidade...'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: -5.090057204817873',
                'step': 'any',
                'min': '-90',
                'max': '90'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: -42.8019123456789',
                'step': 'any',
                'min': '-180',
                'max': '180'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar campos obrigatórios
        self.fields['nome'].required = True
        self.fields['sigla'].required = True
        
        # Adicionar classes de validação
        self.fields['sigla'].widget.attrs['oninput'] = 'this.value = this.value.toUpperCase()'
    
    def clean_sigla(self):
        """Validação da sigla"""
        sigla = self.cleaned_data.get('sigla')
        if sigla:
            sigla = sigla.upper().strip()
            # Verificar se já existe outra sigla igual (exceto a própria instância)
            queryset = Orgao.objects.filter(sigla=sigla)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError('Já existe um órgão com esta sigla.')
        return sigla
    
    def clean_ordem(self):
        """Validação da ordem"""
        ordem = self.cleaned_data.get('ordem')
        if ordem and ordem < 1:
            raise forms.ValidationError('A ordem deve ser um número positivo.')
        return ordem


class GrandeComandoForm(forms.ModelForm):
    """Formulário para gerenciar grandes comandos"""
    
    class Meta:
        model = GrandeComando
        fields = ['orgao', 'nome', 'sigla', 'ordem', 'descricao', 'endereco', 'cidade', 'latitude', 'longitude', 'ativo']
        widgets = {
            'orgao': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Selecione o órgão...'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do grande comando...',
                'maxlength': '200'
            }),
            'sigla': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: CBM, PM, PC, etc...',
                'maxlength': '20',
                'style': 'text-transform: uppercase;'
            }),
            'ordem': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ordem de exibição...',
                'min': '1'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição opcional do grande comando...'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Endereço completo do grande comando...'
            }),
            'cidade': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Selecione a cidade...'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: -5.090057204817873',
                'step': 'any',
                'min': '-90',
                'max': '90'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: -42.8019123456789',
                'step': 'any',
                'min': '-180',
                'max': '180'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['orgao'].queryset = Orgao.objects.filter(ativo=True).order_by('ordem', 'nome')
        self.fields['orgao'].empty_label = "Selecione um órgão..."
        self.fields['sigla'].widget.attrs['oninput'] = 'this.value = this.value.toUpperCase()'
    
    def clean_sigla(self):
        """Validação da sigla"""
        sigla = self.cleaned_data.get('sigla')
        if sigla:
            sigla = sigla.upper().strip()
            orgao = self.cleaned_data.get('orgao')
            if orgao:
                queryset = GrandeComando.objects.filter(orgao=orgao, sigla=sigla)
                if self.instance.pk:
                    queryset = queryset.exclude(pk=self.instance.pk)
                if queryset.exists():
                    raise forms.ValidationError('Já existe um grande comando com esta sigla neste órgão.')
        return sigla


class UnidadeForm(forms.ModelForm):
    """Formulário para gerenciar unidades"""
    
    class Meta:
        model = Unidade
        fields = ['grande_comando', 'nome', 'sigla', 'ordem', 'descricao', 'endereco', 'cidade', 'latitude', 'longitude', 'ativo']
        widgets = {
            'grande_comando': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Selecione o grande comando...'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da unidade...',
                'maxlength': '200'
            }),
            'sigla': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1º BPM, 2º BPM, etc...',
                'maxlength': '20',
                'style': 'text-transform: uppercase;'
            }),
            'ordem': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ordem de exibição...',
                'min': '1'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição opcional da unidade...'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Endereço completo da unidade...'
            }),
            'cidade': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Selecione a cidade...'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: -5.090057204817873',
                'step': 'any',
                'min': '-90',
                'max': '90'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: -42.8019123456789',
                'step': 'any',
                'min': '-180',
                'max': '180'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grande_comando'].queryset = GrandeComando.objects.filter(ativo=True).order_by('orgao__ordem', 'ordem', 'nome')
        self.fields['grande_comando'].empty_label = "Selecione um grande comando..."
        self.fields['sigla'].widget.attrs['oninput'] = 'this.value = this.value.toUpperCase()'
    
    def clean_sigla(self):
        """Validação da sigla"""
        sigla = self.cleaned_data.get('sigla')
        if sigla:
            sigla = sigla.upper().strip()
            grande_comando = self.cleaned_data.get('grande_comando')
            if grande_comando:
                queryset = Unidade.objects.filter(grande_comando=grande_comando, sigla=sigla)
                if self.instance.pk:
                    queryset = queryset.exclude(pk=self.instance.pk)
                if queryset.exists():
                    raise forms.ValidationError('Já existe uma unidade com esta sigla neste grande comando.')
        return sigla


class SubUnidadeForm(forms.ModelForm):
    """Formulário para gerenciar sub-unidades"""
    
    class Meta:
        model = SubUnidade
        fields = ['unidade', 'nome', 'sigla', 'ordem', 'descricao', 'endereco', 'cidade', 'latitude', 'longitude', 'ativo']
        widgets = {
            'unidade': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Selecione a unidade...'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da sub-unidade...',
                'maxlength': '200'
            }),
            'sigla': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1ª Cia, 2ª Cia, etc...',
                'maxlength': '20',
                'style': 'text-transform: uppercase;'
            }),
            'ordem': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ordem de exibição...',
                'min': '1'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição opcional da sub-unidade...'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Endereço completo da sub-unidade...'
            }),
            'cidade': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Selecione a cidade...'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: -5.090057204817873',
                'step': 'any',
                'min': '-90',
                'max': '90'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: -42.8019123456789',
                'step': 'any',
                'min': '-180',
                'max': '180'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unidade'].queryset = Unidade.objects.filter(ativo=True).order_by('grande_comando__orgao__ordem', 'grande_comando__ordem', 'ordem', 'nome')
        self.fields['unidade'].empty_label = "Selecione uma unidade..."
        self.fields['sigla'].widget.attrs['oninput'] = 'this.value = this.value.toUpperCase()'
    
    def clean_sigla(self):
        """Validação da sigla"""
        sigla = self.cleaned_data.get('sigla')
        if sigla:
            sigla = sigla.upper().strip()
            unidade = self.cleaned_data.get('unidade')
            if unidade:
                queryset = SubUnidade.objects.filter(unidade=unidade, sigla=sigla)
                if self.instance.pk:
                    queryset = queryset.exclude(pk=self.instance.pk)
                if queryset.exists():
                    raise forms.ValidationError('Já existe uma sub-unidade com esta sigla nesta unidade.')
        return sigla


class MilitarFuncaoForm(forms.ModelForm):
    """Formulário para gerenciar funções dos militares"""
    
    class Meta:
        model = MilitarFuncao
        fields = ['funcao_militar', 'tipo_funcao', 'status', 'data_inicio', 'data_fim', 'posto_inicial', 'posto_final', 'observacoes', 'ativo']
        widgets = {
            'funcao_militar': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Selecione uma função...'
            }),
            'tipo_funcao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_inicio': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'posto_inicial': forms.Select(attrs={
                'class': 'form-select'
            }),
            'posto_final': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a função...'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset das funções militares
        # Se o usuário tem função do grupo COMISSAO, permitir funções inativas
        from .models import FuncaoMilitar, POSTO_GRADUACAO_CHOICES, UsuarioFuncaoMilitar
        
        # Obter usuário do contexto ou da instância
        usuario = kwargs.get('user')
        if not usuario and hasattr(self, 'instance') and self.instance:
            # Se for MilitarFuncao, obter usuário através do militar
            if hasattr(self.instance, 'militar') and self.instance.militar:
                usuario = getattr(self.instance.militar, 'user', None)
            # Se for UsuarioFuncaoMilitar, obter usuário diretamente
            elif hasattr(self.instance, 'usuario'):
                usuario = self.instance.usuario
        
        if usuario and UsuarioFuncaoMilitar.objects.filter(
            usuario=usuario, 
            ativo=True, 
            funcao_militar__grupo='COMISSAO'
        ).exists():
            # Usuário com função de comissão pode ver todas as funções (incluindo inativas)
            self.fields['funcao_militar'].queryset = FuncaoMilitar.objects.all().order_by('ordem', 'nome')
        else:
            # Usuário comum só vê funções ativas
            self.fields['funcao_militar'].queryset = FuncaoMilitar.objects.filter(ativo=True).order_by('ordem', 'nome')
        
        self.fields['funcao_militar'].empty_label = "Selecione uma função..."
        
        # Configurar opções dos campos de posto
        self.fields['posto_inicial'].choices = [('', 'Selecione...')] + list(POSTO_GRADUACAO_CHOICES)
        self.fields['posto_final'].choices = [('', 'Selecione...')] + list(POSTO_GRADUACAO_CHOICES)
        
        # O campo militar é definido na view, não no formulário
        
        # Se é uma nova função (não tem pk), definir posto inicial como posto atual do militar
        if not self.instance.pk and hasattr(self, 'militar') and self.militar:
            self.fields['posto_inicial'].initial = self.militar.posto_graduacao
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        status = cleaned_data.get('status')
        
        # Validar se data de fim é posterior à data de início
        if data_inicio and data_fim and data_fim < data_inicio:
            raise forms.ValidationError('A data de fim deve ser posterior à data de início.')
        
        # Se é função atual, não deve ter data de fim
        if status == 'ATUAL' and data_fim:
            raise forms.ValidationError('Funções atuais não devem ter data de fim.')
        
        return cleaned_data


class ElogioForm(forms.ModelForm):
    """Formulário para Elogios"""
    
    class Meta:
        model = Elogio
        fields = [
            'militar', 'tipo', 'data_elogio', 'numero_documento', 'descricao', 
            'autoridade_elogiou', 'observacoes'
        ]
        widgets = {
            'militar': forms.Select(attrs={
                'class': 'form-select militar-select2',
                'data-placeholder': 'Digite o nome, matrícula ou posto do militar...',
                'style': 'width: 100%'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_elogio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria 123/2025'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva o motivo do elogio...'
            }),
            'autoridade_elogiou': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da autoridade que elogiou'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais (opcional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar campo militar com queryset filtrado (militares ativos)
        self.fields['militar'].queryset = Militar.objects.filter(classificacao='ATIVO').order_by('nome_guerra')
        self.fields['militar'].required = True
        
        # Configurar campos obrigatórios
        self.fields['tipo'].required = True
        self.fields['data_elogio'].required = True
        self.fields['descricao'].required = True
        self.fields['autoridade_elogiou'].required = True


class PunicaoForm(forms.ModelForm):
    """Formulário para Punições"""
    
    class Meta:
        model = Punicao
        fields = [
            'militar', 'tipo', 'data_punicao', 'numero_documento', 'descricao', 
            'autoridade_puniu', 'periodo_punicao', 'observacoes'
        ]
        widgets = {
            'militar': forms.Select(attrs={
                'class': 'form-select militar-select2',
                'data-placeholder': 'Digite o nome, matrícula ou posto do militar...',
                'style': 'width: 100%'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_punicao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria 123/2025'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva o motivo da punição...'
            }),
            'autoridade_puniu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da autoridade que puniu'
            }),
            'periodo_punicao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 30 dias, 1 ano, etc.'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais (opcional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar campo militar com queryset filtrado (militares ativos)
        self.fields['militar'].queryset = Militar.objects.filter(classificacao='ATIVO').order_by('nome_guerra')
        self.fields['militar'].required = True
        
        # Configurar campos obrigatórios
        self.fields['tipo'].required = True
        self.fields['data_punicao'].required = True
        self.fields['descricao'].required = True
        self.fields['autoridade_puniu'].required = True


class TituloPublicacaoForm(forms.ModelForm):
    class Meta:
        model = TituloPublicacaoConfig
        fields = ['titulo', 'tipo', 'topicos', 'ordem', 'ativo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título da publicação'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'topicos': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ordem': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ordem de exibição (deixe vazio para automático)'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'titulo': 'Título da Publicação',
            'tipo': 'Tipo de Publicação',
            'topicos': 'Tópicos',
            'ordem': 'Ordem de Exibição',
            'ativo': 'Ativo'
        }
        help_texts = {
            'titulo': 'Digite o título completo da publicação',
            'tipo': 'Selecione o tipo de publicação',
            'topicos': 'Digite os tópicos ou descrição da publicação (um por linha)',
            'ordem': 'Ordem de exibição na lista (deixe vazio para ordem automática)',
            'ativo': 'Marque se o título deve estar ativo e visível'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se for um novo título, definir ordem automática
        if not self.instance.pk:
            self.fields['ordem'].required = False
            self.fields['ordem'].widget.attrs['placeholder'] = 'Deixe vazio para ordem automática'


class PublicacaoForm(forms.ModelForm):
    class Meta:
        model = Publicacao
        fields = ['titulo', 'origem_publicacao', 'tipo_publicacao', 'topicos', 'conteudo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título da publicação'
            }),
            'origem_publicacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Comando Geral, DGP, Seção de Promoções',
                'list': 'origem-options',
                'id': 'id_origem_publicacao'
            }),
            'tipo_publicacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria, Instrução, etc.'
            }),
            'topicos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1ª PARTE - SERVIÇOS DIÁRIOS'
            }),
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Digite o conteúdo da publicação'
            })
        }
        labels = {
            'titulo': 'Título',
            'origem_publicacao': 'Origem da Publicação',
            'tipo_publicacao': 'Tipo de Publicação',
            'topicos': 'Tópicos',
            'conteudo': 'Conteúdo'
        }
        help_texts = {
            'titulo': 'Título descritivo da publicação',
            'origem_publicacao': 'Origem da publicação no organograma (ex: Comando Geral, DGP, etc.)',
            'tipo_publicacao': 'Tipo específico da publicação (ex: Portaria, Instrução, etc.)',
            'topicos': 'Tópicos da publicação (ex: 1ª PARTE - SERVIÇOS DIÁRIOS)',
            'conteudo': 'Conteúdo completo da publicação'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tornar todos os campos obrigatórios
        self.fields['titulo'].required = True
        self.fields['origem_publicacao'].required = True
        self.fields['conteudo'].required = True


class ModeloNotaForm(forms.ModelForm):
    """Formulário para modelos de notas"""
    
    class Meta:
        model = ModeloNota
        fields = ['nome', 'descricao', 'tipo_publicacao', 'conteudo', 'padrao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do modelo'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Digite uma descrição para o modelo (opcional)'
            }),
            'tipo_publicacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Digite o conteúdo do modelo'
            }),
            'padrao': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].required = True
        self.fields['conteudo'].required = True


class CaptchaForm(forms.Form):
    """Formulário moderno de captcha - apenas confirmação de que não é robô"""
    
    nao_sou_robo = forms.BooleanField(
        label="",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input modern-checkbox',
            'id': 'id_nao_sou_robo'
        }),
        error_messages={
            'required': 'Você deve confirmar que não é um robô para continuar.'
        }
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nao_sou_robo'].widget.attrs.update({
            'onchange': 'validateModernCaptcha()'
        })


class AfastamentoForm(forms.ModelForm):
    """Formulário para gerenciar afastamentos dos militares"""
    
    class Meta:
        model = Afastamento
        fields = [
            'militar', 'tipo_afastamento', 'data_inicio', 'data_fim_prevista', 
            'data_fim_real', 'status', 'motivo', 'observacoes', 
            'documento_referencia', 'numero_documento'
        ]
        widgets = {
            'militar': forms.Select(attrs={
                'class': 'form-select militar-select2',
                'data-placeholder': 'Digite o nome, matrícula ou posto do militar...',
                'style': 'width: 100%'
            }),
            'tipo_afastamento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_inicio': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'onchange': 'calcularDias()'
                }
            ),
            'data_fim_prevista': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'onchange': 'calcularDias()'
                }
            ),
            'data_fim_real': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'onchange': 'calcularDias()'
                }
            ),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva o motivo do afastamento...'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais...'
            }),
            'documento_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria, Ofício, etc.'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do documento'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair request se fornecido
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Atualizar choices do tipo de afastamento - usar exatamente os mesmos da situação
        from .models import Afastamento
        # Usar os mesmos tipos que estão no campo situação do modelo Militar
        tipos_afastamento = Afastamento.get_all_tipo_choices()
        # Atualizar choices do campo (incluindo opção vazia no início)
        self.fields['tipo_afastamento'].choices = [('', '---------')] + tipos_afastamento
        
        # Aplicar filtro hierárquico no queryset de militares
        from .permissoes_hierarquicas import obter_funcao_militar_ativa
        from .filtros_hierarquicos import aplicar_filtro_hierarquico_militares
        
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        from django.db.models import Case, When, Value, IntegerField, Q
        hierarquia_ordem = Case(
            *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        
        # Base queryset de militares ativos
        militares_queryset = Militar.objects.filter(
            classificacao='ATIVO'
        ).annotate(
            ordem_hierarquia=hierarquia_ordem
        )
        
        # Aplicar filtro hierárquico se houver request
        if self.request:
            funcao_usuario = obter_funcao_militar_ativa(self.request.user)
            militares_queryset = aplicar_filtro_hierarquico_militares(militares_queryset, funcao_usuario, self.request.user)
        
        # Ordenar por hierarquia
        militares_queryset = militares_queryset.order_by(
            'ordem_hierarquia',
            'data_promocao_atual',
            'numeracao_antiguidade',
            'nome_completo'
        )
        
        # Garantir que o campo nunca esteja desabilitado ou readonly
        self.fields['militar'].widget.attrs.pop('disabled', None)
        self.fields['militar'].widget.attrs.pop('readonly', None)
        
        # Tornar o campo militar obrigatório apenas na criação
        if not self.instance.pk:
            self.fields['militar'].required = True
        else:
            # Na edição, permitir editar o militar
            self.fields['militar'].required = False
        
        # Para permitir que o Select2 AJAX funcione corretamente,
        # sempre usar um queryset amplo (todos os militares ativos)
        # A validação hierárquica será feita no clean_militar
        # Isso evita o erro "Faça uma escolha válida" quando o Select2 retorna militares via AJAX
        # que podem não estar no queryset filtrado inicial
        queryset_amplo = Militar.objects.filter(
            classificacao='ATIVO'
        ).annotate(
            ordem_hierarquia=hierarquia_ordem
        ).order_by(
            'ordem_hierarquia',
            'data_promocao_atual',
            'numeracao_antiguidade',
            'nome_completo'
        )
        
        # Se está editando e o militar atual não está no queryset amplo, adicioná-lo
        if self.instance.pk and self.instance.militar:
            militar_atual = self.instance.militar
            if not queryset_amplo.filter(id=militar_atual.id).exists():
                # Adicionar o militar atual ao queryset
                militares_ids = list(queryset_amplo.values_list('id', flat=True))
                militares_ids.append(militar_atual.id)
                queryset_amplo = Militar.objects.filter(id__in=militares_ids).annotate(
                    ordem_hierarquia=hierarquia_ordem
                ).order_by(
                    'ordem_hierarquia',
                    'data_promocao_atual',
                    'numeracao_antiguidade',
                    'nome_completo'
                )
        
        # Sempre usar queryset amplo - validação hierárquica será feita no clean_militar
        self.fields['militar'].queryset = queryset_amplo
    
    def clean_militar(self):
        """
        Validação do militar - aceita qualquer militar válido dentro do escopo hierárquico.
        Os filtros hierárquicos já são aplicados no queryset do campo.
        """
        militar = self.cleaned_data.get('militar')
        if militar:
            # Se já é um objeto Militar, verificar se existe e está ativo
            if hasattr(militar, 'id'):
                try:
                    militar_obj = Militar.objects.get(id=militar.id, classificacao='ATIVO')
                    # Verificar se o militar está dentro do escopo hierárquico do usuário
                    if self.request:
                        from .permissoes_hierarquicas import obter_funcao_militar_ativa
                        from .filtros_hierarquicos import aplicar_filtro_hierarquico_militares
                        funcao_usuario = obter_funcao_militar_ativa(self.request.user)
                        if funcao_usuario:
                            # Verificar se o militar está no queryset filtrado
                            militares_queryset = Militar.objects.filter(classificacao='ATIVO')
                            militares_filtrados = aplicar_filtro_hierarquico_militares(militares_queryset, funcao_usuario, self.request.user)
                            if not militares_filtrados.filter(id=militar_obj.id).exists():
                                # Se não está no escopo, verificar se é superusuário
                                if not self.request.user.is_superuser:
                                    raise forms.ValidationError('Você não tem permissão para criar afastamento para este militar.')
                    return militar_obj
                except Militar.DoesNotExist:
                    raise forms.ValidationError('Militar selecionado não encontrado ou não está ativo.')
            # Se é um ID (string ou número), buscar o militar
            else:
                try:
                    militar_obj = Militar.objects.get(id=militar, classificacao='ATIVO')
                    # Verificar escopo hierárquico
                    if self.request:
                        from .permissoes_hierarquicas import obter_funcao_militar_ativa
                        from .filtros_hierarquicos import aplicar_filtro_hierarquico_militares
                        funcao_usuario = obter_funcao_militar_ativa(self.request.user)
                        if funcao_usuario:
                            militares_queryset = Militar.objects.filter(classificacao='ATIVO')
                            militares_filtrados = aplicar_filtro_hierarquico_militares(militares_queryset, funcao_usuario, self.request.user)
                            if not militares_filtrados.filter(id=militar_obj.id).exists():
                                if not self.request.user.is_superuser:
                                    raise forms.ValidationError('Você não tem permissão para criar afastamento para este militar.')
                    return militar_obj
                except (Militar.DoesNotExist, ValueError):
                    raise forms.ValidationError('Militar selecionado não encontrado ou não está ativo.')
        return militar
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim_prevista = cleaned_data.get('data_fim_prevista')
        data_fim_real = cleaned_data.get('data_fim_real')
        militar = cleaned_data.get('militar')
        
        # Validar se data de fim prevista é posterior à data de início
        if data_inicio and data_fim_prevista and data_fim_prevista < data_inicio:
            raise forms.ValidationError('A data de fim prevista deve ser posterior à data de início.')
        
        # Validar se data de fim real é posterior à data de início
        if data_inicio and data_fim_real and data_fim_real < data_inicio:
            raise forms.ValidationError('A data de fim real deve ser posterior à data de início.')
        
        # Verificação de choque de datas removida - apenas filtros hierárquicos e permissões são aplicados
        
        return cleaned_data


class AverbacaoForm(forms.ModelForm):
    """Formulário para gerenciar averbações de tempo de contribuição dos militares"""
    
    class Meta:
        model = Averbacao
        fields = [
            'militar', 'tempo_contribuicao_dias', 'aproveitamento_dias',
            'numero_ctc_inss', 'documento_publicacao', 'assinado_por_nome', 'assinado_por_cargo',
            'orgao_local', 'endereco_orgao', 'cep_orgao', 'cidade_estado_orgao',
            'data_averbacao', 'observacoes'
        ]
        widgets = {
            'militar': forms.Select(attrs={
                'class': 'form-select militar-select2',
                'data-placeholder': 'Digite o nome, matrícula ou posto do militar...',
                'style': 'width: 100%'
            }),
            'tempo_contribuicao_dias': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'onchange': 'calcularTempoFormatado()'
            }),
            'aproveitamento_dias': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'onchange': 'calcularTempoFormatado()'
            }),
            'numero_ctc_inss': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 0020469543'
            }),
            'documento_publicacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria Nº 123/2024, Boletim Especial Nº 456/2024'
            }),
            'assinado_por_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo da pessoa que assinou'
            }),
            'assinado_por_cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Presidente do INSS'
            }),
            'orgao_local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: TERESINA - AGÊNCIA DA PREVIDÊNCIA SOCIAL TERESINA - LESTE'
            }),
            'endereco_orgao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Endereço completo do órgão'
            }),
            'cep_orgao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 64051005',
                'maxlength': '10'
            }),
            'cidade_estado_orgao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: TERESINA - PI'
            }),
            'data_averbacao': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações adicionais...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset do militar
        from .models import Militar
        if not self.instance.pk:
            # Se está criando, permitir qualquer militar ativo
            ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
            from django.db.models import Case, When, Value, IntegerField
            hierarquia_ordem = Case(
                *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
                default=Value(len(ordem_hierarquica)),
                output_field=IntegerField()
            )
            self.fields['militar'].queryset = Militar.objects.filter(
                classificacao='ATIVO'
            ).annotate(
                ordem_hierarquia=hierarquia_ordem
            ).order_by(
                'ordem_hierarquia',
                'data_promocao_atual',
                'numeracao_antiguidade',
                'nome_completo'
            )
        else:
            # Se está editando, incluir o militar atual
            if self.instance.militar:
                from django.db.models import Q
                ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
                from django.db.models import Case, When, Value, IntegerField
                hierarquia_ordem = Case(
                    *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
                    default=Value(len(ordem_hierarquica)),
                    output_field=IntegerField()
                )
                self.fields['militar'].queryset = Militar.objects.filter(
                    Q(id=self.instance.militar.id) | Q(classificacao='ATIVO')
                ).annotate(
                    ordem_hierarquia=hierarquia_ordem
                ).order_by(
                    'ordem_hierarquia',
                    'data_promocao_atual',
                    'numeracao_antiguidade',
                    'nome_completo'
                )
            else:
                ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
                from django.db.models import Case, When, Value, IntegerField
                hierarquia_ordem = Case(
                    *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
                    default=Value(len(ordem_hierarquica)),
                    output_field=IntegerField()
                )
                self.fields['militar'].queryset = Militar.objects.filter(
                    classificacao='ATIVO'
                ).annotate(
                    ordem_hierarquia=hierarquia_ordem
                ).order_by(
                    'ordem_hierarquia',
                    'data_promocao_atual',
                    'numeracao_antiguidade',
                    'nome_completo'
                )
    
    def clean(self):
        cleaned_data = super().clean()
        tempo_contribuicao = cleaned_data.get('tempo_contribuicao_dias')
        aproveitamento = cleaned_data.get('aproveitamento_dias')
        
        # Validar que os dias não sejam negativos
        if tempo_contribuicao is not None and tempo_contribuicao < 0:
            raise forms.ValidationError('O tempo de contribuição não pode ser negativo.')
        
        if aproveitamento is not None and aproveitamento < 0:
            raise forms.ValidationError('O aproveitamento não pode ser negativo.')
        
        return cleaned_data


class DocumentoAfastamentoForm(forms.ModelForm):
    """Formulário para upload de documentos de afastamento"""
    
    class Meta:
        model = DocumentoAfastamento
        fields = ['tipo', 'titulo', 'descricao', 'arquivo']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria de Afastamento 123/2024'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do documento...'
            }),
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            }),
        }
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            if arquivo.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError("O arquivo deve ter no máximo 10MB.")
            
            extensoes_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            nome_arquivo = arquivo.name.lower()
            if not any(nome_arquivo.endswith(ext) for ext in extensoes_permitidas):
                raise forms.ValidationError(f"Formato de arquivo não permitido. Use: {', '.join(extensoes_permitidas)}")
        
        return arquivo


class FeriasForm(forms.ModelForm):
    """Formulário para gerenciar férias dos militares"""
    
    class Meta:
        model = Ferias
        fields = [
            'plano', 'militar', 'tipo', 'ano_referencia', 'data_inicio', 'data_fim', 
            'quantidade_dias', 'status', 'observacoes', 
            'documento_referencia', 'numero_documento'
        ]
        widgets = {
            'militar': forms.Select(attrs={
                'class': 'form-select militar-select2',
                'data-placeholder': 'Digite o nome, matrícula ou posto do militar...',
                'style': 'width: 100%'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ano_referencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000,
                'max': 2100
            }),
            'data_inicio': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'onchange': 'calcularDiasFerias()'
                }
            ),
            'data_fim': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'onchange': 'calcularDiasFerias()'
                }
            ),
            'quantidade_dias': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 30
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais...'
            }),
            'documento_referencia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: DOE n° 001/2025 de 25/01/2025'
            }),
            'plano': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        plano_id = kwargs.pop('plano_id', None)
        super().__init__(*args, **kwargs)
        
        # Definir valor padrão de 30 dias se for um novo registro
        if not self.instance.pk and 'quantidade_dias' in self.fields:
            self.fields['quantidade_dias'].initial = 30
        
        # Garantir que o campo tipo tenha um valor padrão se for um novo registro
        if 'tipo' in self.fields:
            # Tornar o campo obrigatório
            self.fields['tipo'].required = True
            
            # Sempre definir INTEGRAL como padrão para novos registros
            if not self.instance.pk:
                self.fields['tipo'].initial = 'INTEGRAL'
            
            # Garantir que o campo tenha um valor válido mesmo se não for enviado
            if self.data and 'tipo' in self.data and not self.data['tipo']:
                # Se o campo foi enviado vazio, usar INTEGRAL
                self.data = self.data.copy()
                self.data['tipo'] = 'INTEGRAL'
        
        # Configurar campo documento_referencia como select com opções específicas
        if 'documento_referencia' in self.fields:
            DOCUMENTO_REFERENCIA_CHOICES = [
                ('', 'Selecione...'),
                ('BOLETIM_OSTENSIVO', 'Boletim Ostensivo'),
                ('BOLETIM_RESERVADO', 'Boletim Reservado'),
                ('DIARIO_OFICIAL_ESTADO', 'Diário Oficial do Estado'),
            ]
            self.fields['documento_referencia'] = forms.ChoiceField(
                choices=DOCUMENTO_REFERENCIA_CHOICES,
                required=False,
                widget=forms.Select(attrs={'class': 'form-select'}),
                label='Documento de Referência'
            )
            # Se já existe um valor, tentar manter
            if self.instance.pk and self.instance.documento_referencia:
                # Se o valor atual não estiver nas opções, criar uma opção temporária
                valor_atual = self.instance.documento_referencia
                if valor_atual not in [choice[0] for choice in DOCUMENTO_REFERENCIA_CHOICES]:
                    choices_com_valor_atual = DOCUMENTO_REFERENCIA_CHOICES + [(valor_atual, valor_atual)]
                    self.fields['documento_referencia'].choices = choices_com_valor_atual
                    self.fields['documento_referencia'].initial = valor_atual
        
        # Configurar campo plano
        if 'plano' in self.fields:
            self.fields['plano'].required = False
            self.fields['plano'].queryset = PlanoFerias.objects.all().order_by('-ano_plano', '-ano_referencia')
            self.fields['plano'].empty_label = "Nenhum plano (férias individual)"
            
            # Se plano_id foi passado, definir o valor e ocultar o campo
            if plano_id:
                self.fields['plano'].widget = forms.HiddenInput()
                self.fields['plano'].initial = plano_id
        
        # Tornar o campo militar obrigatório apenas na criação
        if not self.instance.pk:
            self.fields['militar'].required = True
            # Ordenar militares por hierarquia (posto) e depois por antiguidade
            ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
            from django.db.models import Case, When, Value, IntegerField
            hierarquia_ordem = Case(
                *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
                default=Value(len(ordem_hierarquica)),
                output_field=IntegerField()
            )
            # Incluir todos os militares ativos no queryset para validação
            self.fields['militar'].queryset = Militar.objects.filter(
                classificacao='ATIVO'
            ).annotate(
                ordem_hierarquia=hierarquia_ordem
            ).order_by(
                'ordem_hierarquia',
                'data_promocao_atual',
                'numeracao_antiguidade',
                'nome_completo'
            )
            
            # Definir ano padrão como o ano atual
            from datetime import datetime
            self.fields['ano_referencia'].initial = datetime.now().year
        else:
            self.fields['militar'].required = False
            # Se está editando, incluir o militar atual no queryset
            if self.instance.militar:
                # Ordenar militares por hierarquia (posto) e depois por antiguidade
                ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
                
                from django.db.models import Case, When, Value, IntegerField, Q
                hierarquia_ordem = Case(
                    *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
                    default=Value(len(ordem_hierarquica)),
                    output_field=IntegerField()
                )
                
                # Incluir o militar atual e todos os ativos no queryset para validação
                self.fields['militar'].queryset = Militar.objects.filter(
                    Q(id=self.instance.militar.id) | Q(classificacao='ATIVO')
                ).annotate(
                    ordem_hierarquia=hierarquia_ordem
                ).order_by(
                    'ordem_hierarquia',
                    'data_promocao_atual',
                    'numeracao_antiguidade',
                    'nome_completo'
                )
    
    def clean_tipo(self):
        """Validação do campo tipo"""
        tipo = self.cleaned_data.get('tipo')
        if not tipo:
            raise forms.ValidationError("O tipo de férias é obrigatório.")
        
        # Verificar se o tipo está nas opções válidas
        tipos_validos = [choice[0] for choice in Ferias.TIPO_CHOICES]
        if tipo not in tipos_validos:
            raise forms.ValidationError(f"Tipo de férias inválido. Escolha entre: {', '.join([choice[1] for choice in Ferias.TIPO_CHOICES])}")
        
        return tipo
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        quantidade_dias = cleaned_data.get('quantidade_dias')
        militar = cleaned_data.get('militar')
        
        if data_inicio and data_fim:
            if data_fim < data_inicio:
                raise forms.ValidationError("A data de fim deve ser posterior à data de início.")
            
            dias_calculados = (data_fim - data_inicio).days + 1
            if quantidade_dias and dias_calculados != quantidade_dias:
                # Atualizar quantidade_dias automaticamente
                cleaned_data['quantidade_dias'] = dias_calculados
        
        # Verificar choque de datas com outros afastamentos
        if militar and data_inicio and data_fim:
            choques = verificar_choque_datas_afastamentos(militar, data_inicio, data_fim, instance=self.instance)
            if choques:
                mensagem = "<strong>⚠️ ATENÇÃO: Há choque de datas com os seguintes afastamentos:</strong><br><br>"
                mensagem += "<ul style='margin-bottom: 0;'>"
                mensagem += "".join(f"<li>{choque}</li>" for choque in choques)
                mensagem += "</ul><br>"
                mensagem += "<strong>Por favor, ajuste as datas para evitar o choque ou cancele/reprograme os afastamentos conflitantes.</strong>"
                raise forms.ValidationError(mensagem)
        
        return cleaned_data


class DocumentoFeriasForm(forms.ModelForm):
    """Formulário para upload de documentos de férias"""
    
    class Meta:
        model = DocumentoFerias
        fields = ['tipo', 'titulo', 'descricao', 'arquivo']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria de Férias 123/2024'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do documento...'
            }),
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            }),
        }
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            if arquivo.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError("O arquivo deve ter no máximo 10MB.")
            
            extensoes_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            nome_arquivo = arquivo.name.lower()
            if not any(nome_arquivo.endswith(ext) for ext in extensoes_permitidas):
                raise forms.ValidationError(
                    "Formato de arquivo não permitido. Use: PDF, JPG, PNG, DOC, DOCX"
                )
        
        return arquivo


class PlanoFeriasForm(forms.ModelForm):
    """Formulário para gerenciar planos de férias"""
    
    class Meta:
        model = PlanoFerias
        fields = [
            'ano_referencia', 'ano_plano', 'titulo', 'descricao', 'status',
            'documento_referencia', 'numero_documento'
        ]
        widgets = {
            'ano_referencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000,
                'max': 2100
            }),
            'ano_plano': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000,
                'max': 2100
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Plano de Férias 2025'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição do plano de férias...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'documento_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria, Decreto, etc.'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do documento'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from datetime import datetime
        ano_atual = datetime.now().year
        
        # Se for edição (já tem pk), remover o campo status do formulário
        if self.instance.pk:
            # Remover o campo status da edição - status só pode ser alterado pela aprovação
            if 'status' in self.fields:
                del self.fields['status']
        else:
            # Na criação, definir ano do plano como o ano atual
            self.fields['ano_plano'].initial = ano_atual
            self.fields['ano_referencia'].initial = ano_atual
            self.fields['titulo'].initial = f'Plano de Férias {ano_atual}'
    
    def clean(self):
        cleaned_data = super().clean()
        ano_referencia = cleaned_data.get('ano_referencia')
        ano_plano = cleaned_data.get('ano_plano')
        
        if ano_referencia and ano_plano:
            if ano_referencia < ano_plano - 1:
                raise forms.ValidationError("O ano de referência não pode ser muito anterior ao ano do plano.")
        
        return cleaned_data


class TrocaOleoViaturaForm(forms.ModelForm):
    """Formulário para cadastro e edição de trocas de óleo de viaturas"""
    
    class Meta:
        from .models import TrocaOleoViatura
        model = TrocaOleoViatura
        fields = [
            'viatura', 'data_troca', 'km_troca', 'tipo_oleo', 'nome_oleo', 'quantidade_litros',
            'valor_litro', 'valor_total', 'valor_total_nota', 'fornecedor_oficina', 'trocou_filtro_oleo',
            'valor_filtro_oleo', 'trocou_filtro_combustivel', 'valor_filtro_combustivel',
            'trocou_filtro_ar', 'valor_filtro_ar', 'adicionou_aditivo_arrefecimento',
            'quantidade_aditivo_arrefecimento', 'valor_aditivo_arrefecimento',
            'outras_pecas', 'valor_outras_pecas', 'proximo_km_troca', 'responsavel', 'observacoes', 'ativo'
        ]
        widgets = {
            'viatura': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'data_troca': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'id': 'id_data_troca'
            }),
            'km_troca': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'KM no momento da troca'
            }),
            'tipo_oleo': forms.Select(attrs={'class': 'form-select'}),
            'nome_oleo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Óleo Mobil 10W-40, Shell Helix, etc.'
            }),
            'quantidade_litros': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Ex: 5.00'
            }),
            'valor_litro': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_litro',
                'placeholder': 'Digite o valor',
                'type': 'text'
            }),
            'valor_total': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_total',
                'placeholder': 'Será calculado automaticamente',
                'readonly': True,
                'type': 'text'
            }),
            'valor_total_nota': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_total_nota',
                'placeholder': 'Será calculado automaticamente',
                'readonly': True,
                'type': 'text'
            }),
            'fornecedor_oficina': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da oficina ou fornecedor'
            }),
            'trocou_filtro_oleo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_trocou_filtro_oleo',
            }),
            'valor_filtro_oleo': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_filtro_oleo',
                'placeholder': 'Valor do filtro de óleo (se trocado)',
                'type': 'text'
            }),
            'trocou_filtro_combustivel': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_trocou_filtro_combustivel',
            }),
            'valor_filtro_combustivel': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_filtro_combustivel',
                'placeholder': 'Valor do filtro de combustível (se trocado)',
                'type': 'text'
            }),
            'trocou_filtro_ar': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_trocou_filtro_ar',
            }),
            'valor_filtro_ar': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_filtro_ar',
                'placeholder': 'Valor do filtro de ar condicionado (se trocado)',
                'type': 'text'
            }),
            'adicionou_aditivo_arrefecimento': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_adicionou_aditivo_arrefecimento',
            }),
            'quantidade_aditivo_arrefecimento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Quantidade em litros',
                'id': 'id_quantidade_aditivo_arrefecimento',
            }),
            'valor_aditivo_arrefecimento': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_aditivo_arrefecimento',
                'placeholder': 'Valor do aditivo de arrefecimento',
                'type': 'text'
            }),
            'outras_pecas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Liste outras peças trocadas com nome e valor. Ex:\n- Pastilha de freio dianteira: R$ 150,00\n- Correia alternador: R$ 80,00'
            }),
            'valor_outras_pecas': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_outras_pecas',
                'placeholder': 'Valor total das outras peças',
                'type': 'text'
            }),
            'proximo_km_troca': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'KM previsto para próxima troca'
            }),
            'responsavel': forms.Select(attrs={
                'class': 'form-select militar-select2',
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a troca de óleo...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Viatura, Militar
        
        # Filtrar apenas viaturas ativas
        self.fields['viatura'].queryset = Viatura.objects.filter(ativo=True).order_by('placa')
        
        # Filtrar apenas militares ativos e ordenar por posto e nome
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        from django.db.models import Case, When, Value, IntegerField
        hierarquia_ordem = Case(
            *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        militares_queryset = Militar.objects.filter(
            classificacao='ATIVO'
        ).annotate(
            ordem_hierarquia=hierarquia_ordem
        ).order_by('ordem_hierarquia', 'nome_completo')
        
        self.fields['responsavel'].queryset = militares_queryset
    
    def clean_valor_total(self):
        """Validação e formatação do valor total"""
        valor = self.cleaned_data.get('valor_total', '')
        if isinstance(valor, str):
            # Remover formatação (pontos e vírgulas)
            valor = valor.replace('.', '').replace(',', '.')
            try:
                valor = float(valor)
            except (ValueError, TypeError):
                valor = None
        return valor
    
    def clean(self):
        """Validações gerais"""
        cleaned_data = super().clean()
        quantidade = cleaned_data.get('quantidade_litros')
        valor_litro = cleaned_data.get('valor_litro')
        valor_filtro_oleo = cleaned_data.get('valor_filtro_oleo', 0) or 0
        valor_filtro_combustivel = cleaned_data.get('valor_filtro_combustivel', 0) or 0
        valor_filtro_ar = cleaned_data.get('valor_filtro_ar', 0) or 0
        valor_aditivo_arrefecimento = cleaned_data.get('valor_aditivo_arrefecimento', 0) or 0
        valor_outras_pecas = cleaned_data.get('valor_outras_pecas', 0) or 0
        valor_total = cleaned_data.get('valor_total')
        
        # Converter valores se forem strings
        def converter_valor(valor):
            if isinstance(valor, str):
                valor = valor.replace('.', '').replace(',', '.')
                try:
                    return float(valor) if valor else 0
                except:
                    return 0
            return float(valor) if valor else 0
        
        valor_litro = converter_valor(valor_litro) if valor_litro else None
        valor_filtro_oleo = converter_valor(valor_filtro_oleo)
        valor_filtro_combustivel = converter_valor(valor_filtro_combustivel)
        valor_filtro_ar = converter_valor(valor_filtro_ar)
        valor_aditivo_arrefecimento = converter_valor(valor_aditivo_arrefecimento)
        valor_outras_pecas = converter_valor(valor_outras_pecas)
        
        # Calcular valor total se tiver quantidade e valor por litro
        if quantidade and valor_litro:
            valor_calculado = float(quantidade) * float(valor_litro)
            valor_calculado += valor_filtro_oleo
            valor_calculado += valor_filtro_combustivel
            valor_calculado += valor_filtro_ar
            valor_calculado += valor_aditivo_arrefecimento
            valor_calculado += valor_outras_pecas
            
            # Atualizar valor_total se não estiver definido ou se estiver diferente
            if not valor_total:
                cleaned_data['valor_total'] = valor_calculado
            elif abs(float(valor_total) - float(valor_calculado)) > 0.01:
                # Permitir pequenas diferenças de arredondamento
                cleaned_data['valor_total'] = valor_calculado
            
            # O valor_total_nota é igual ao valor_total (soma de tudo)
            cleaned_data['valor_total_nota'] = valor_calculado
        
        # Validar que KM não seja menor que o anterior
        viatura = cleaned_data.get('viatura')
        km_troca = cleaned_data.get('km_troca')
        
        if viatura and km_troca:
            from .models import TrocaOleoViatura
            instance_pk = self.instance.pk if self.instance else None
            trocas_anteriores = TrocaOleoViatura.objects.filter(
                viatura=viatura,
                ativo=True
            ).exclude(pk=instance_pk)
            
            if trocas_anteriores.exists():
                km_anterior = trocas_anteriores.order_by('-data_troca', '-km_troca').first().km_troca
                if km_troca < km_anterior:
                    from django.core.exceptions import ValidationError
                    raise ValidationError(
                        {'km_troca': f"O KM da troca de óleo ({km_troca}) não pode ser menor que o KM da última troca registrada ({km_anterior})."}
                    )
        
        return cleaned_data


class LicenciamentoViaturaForm(forms.ModelForm):
    """Formulário para cadastro e edição de licenciamentos de viaturas"""
    
    class Meta:
        from .models import LicenciamentoViatura
        model = LicenciamentoViatura
        fields = [
            'viatura', 'ano_licenciamento', 'data_vencimento', 'valor_licenciamento',
            'data_pagamento', 'status', 'proximo_vencimento', 'responsavel', 'observacoes', 'ativo'
        ]
        widgets = {
            'viatura': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'ano_licenciamento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1900',
                'max': '2100',
                'placeholder': 'Ex: 2025'
            }),
            'data_vencimento': DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'valor_licenciamento': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_licenciamento',
                'placeholder': 'Digite o valor',
                'type': 'text'
            }),
            'data_pagamento': DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'proximo_vencimento': DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'responsavel': forms.Select(attrs={
                'class': 'form-select militar-select2',
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre o licenciamento...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Viatura, Militar
        
        # Filtrar apenas viaturas ativas
        self.fields['viatura'].queryset = Viatura.objects.filter(ativo=True).order_by('placa')
        
        # Filtrar apenas militares ativos para responsável
        self.fields['responsavel'].queryset = Militar.objects.filter(
            classificacao='ATIVO'
        ).order_by('posto_graduacao', 'nome_completo')
        
        # Definir ano atual como padrão se for criação
        if not self.instance.pk:
            from datetime import date
            self.fields['ano_licenciamento'].initial = date.today().year
        
        # Garantir que os widgets de data usem o formato correto
        # O DateInput customizado já tem format_value que converte automaticamente
        if self.instance and self.instance.pk:
            # Garantir que os widgets estejam configurados corretamente
            self.fields['data_vencimento'].widget.format = '%Y-%m-%d'
            self.fields['data_pagamento'].widget.format = '%Y-%m-%d'
            self.fields['proximo_vencimento'].widget.format = '%Y-%m-%d'
    
    def clean_valor_licenciamento(self):
        """Converte valor formatado em BRL para formato numérico"""
        valor = self.cleaned_data.get('valor_licenciamento', '')
        
        if not valor or valor == '':
            raise forms.ValidationError("Este campo é obrigatório.")
        
        if isinstance(valor, str):
            valor_limpo = valor.replace('R$', '').replace(' ', '').strip()
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
            
            try:
                return float(valor_limpo)
            except (ValueError, TypeError):
                raise forms.ValidationError("Valor inválido. Use o formato: 500,00 ou 500.00")
        
        return valor
    
    def clean(self):
        """Validações gerais"""
        cleaned_data = super().clean()
        data_vencimento = cleaned_data.get('data_vencimento')
        data_pagamento = cleaned_data.get('data_pagamento')
        ano_licenciamento = cleaned_data.get('ano_licenciamento')
        
        # Validar que data de pagamento não seja futura
        if data_pagamento:
            from datetime import date
            if data_pagamento > date.today():
                from django.core.exceptions import ValidationError
                raise ValidationError({
                    'data_pagamento': 'A data de pagamento não pode ser futura.'
                })
        
        # Validar relação entre ano de licenciamento e data de vencimento
        if data_vencimento and ano_licenciamento:
            ano_vencimento = data_vencimento.year
            if abs(ano_licenciamento - ano_vencimento) > 1:
                from django.core.exceptions import ValidationError
                raise ValidationError({
                    'ano_licenciamento': 'O ano de licenciamento deve estar próximo ao ano de vencimento.'
                })
        
        # Atualizar status automaticamente
        if data_vencimento:
            from datetime import date
            hoje = date.today()
            if data_pagamento:
                cleaned_data['status'] = 'PAGO'
            elif data_vencimento < hoje:
                cleaned_data['status'] = 'VENCIDO'
            elif cleaned_data.get('status') != 'PAGO':
                cleaned_data['status'] = 'PENDENTE'
        
        return cleaned_data


class ViaturaForm(forms.ModelForm):
    """Formulário para cadastro e edição de viaturas"""
    
    # Campo para seleção hierárquica do organograma (não é salvo diretamente)
    organograma_select = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'organograma-select'
        })
    )
    
    class Meta:
        model = Viatura
        fields = [
            'prefixo', 'placa', 'tipo', 'marca', 'modelo', 'ano_fabricacao', 'ano_modelo',
            'chassi', 'renavam', 'cor', 'km_atual', 'status', 'combustivel',
            'capacidade_tanque', 'cartao_abastecimento', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'observacoes', 'data_aquisicao', 'valor_aquisicao', 'fornecedor', 'ativo'
        ]
        widgets = {
            'prefixo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: ABC, DEF, GHI',
                'style': 'text-transform: uppercase;'
            }),
            'placa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ABC-1234 ou ABC1D23',
                'style': 'text-transform: uppercase;'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Ford, Chevrolet'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Ranger, D20'
            }),
            'ano_fabricacao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1900',
                'max': '2100'
            }),
            'ano_modelo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1900',
                'max': '2100'
            }),
            'chassi': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do chassi'
            }),
            'renavam': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do RENAVAM'
            }),
            'cor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Branco, Vermelho'
            }),
            'km_atual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'combustivel': forms.Select(attrs={'class': 'form-select'}),
            'capacidade_tanque': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Ex: 50.00'
            }),
            'cartao_abastecimento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do cartão de abastecimento'
            }),
            'orgao': forms.HiddenInput(),
            'grande_comando': forms.HiddenInput(),
            'unidade': forms.HiddenInput(),
            'sub_unidade': forms.HiddenInput(),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações sobre a viatura...'
            }),
            'data_aquisicao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'valor_aquisicao': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_aquisicao',
                'placeholder': 'Digite o valor',
                'type': 'text'
            }),
            'fornecedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do fornecedor'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair request do kwargs se presente
        self.request = kwargs.pop('request', None)
        
        super().__init__(*args, **kwargs)
        # Tornar organizações não obrigatórias no formulário (validação será feita no model)
        self.fields['orgao'].required = False
        self.fields['grande_comando'].required = False
        self.fields['unidade'].required = False
        self.fields['sub_unidade'].required = False
        
        # Campos de organização ficam ocultos (serão preenchidos via JavaScript)
        self.fields['orgao'].widget = forms.HiddenInput()
        self.fields['grande_comando'].widget = forms.HiddenInput()
        self.fields['unidade'].widget = forms.HiddenInput()
        self.fields['sub_unidade'].widget = forms.HiddenInput()
        
        # Campo organograma_select não está no model, então precisa ser adicionado manualmente
        if 'organograma_select' not in self.fields:
            self.fields['organograma_select'] = forms.CharField(
                required=False,
                widget=forms.Select(attrs={
                    'class': 'form-select',
                    'id': 'organograma-select'
                })
            )
        
        # Tornar km_atual somente leitura na edição (exceto para superusuários)
        if self.instance and self.instance.pk:  # Está editando uma viatura existente
            if not (self.request and self.request.user.is_superuser):
                # Tornar o campo somente leitura
                self.fields['km_atual'].widget.attrs['readonly'] = True
                self.fields['km_atual'].widget.attrs['class'] = 'form-control bg-light'
                self.fields['km_atual'].required = False
        
        # Garantir que o campo de data de aquisição tenha o formato correto para input type="date"
        if 'data_aquisicao' in self.fields:
            # Configurar widget para formato ISO
            self.fields['data_aquisicao'].widget = forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_data_aquisicao'
            })
            self.fields['data_aquisicao'].widget.format = '%Y-%m-%d'
            
            # Se houver uma instância (edição), garantir que o valor esteja no formato correto
            if self.instance and self.instance.pk and self.instance.data_aquisicao:
                # Definir o valor inicial no formato ISO
                try:
                    self.initial['data_aquisicao'] = self.instance.data_aquisicao.strftime('%Y-%m-%d')
                except:
                    pass


class ViaturaTransferenciaForm(forms.Form):
    """Formulário para transferência de viaturas entre unidades"""
    
    # Campo para seleção hierárquica do organograma de destino
    organograma_destino = forms.CharField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'organograma-destino-select'
        })
    )
    
    justificativa = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Informe o motivo da transferência...'
        }),
        label='Justificativa',
        help_text='Motivo obrigatório para a transferência da viatura'
    )
    
    observacoes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observações adicionais sobre a transferência...'
        }),
        label='Observações'
    )
    
    def __init__(self, *args, **kwargs):
        self.viatura = kwargs.pop('viatura', None)
        super().__init__(*args, **kwargs)
        
        # Campos ocultos para armazenar os valores da organização de destino
        self.fields['orgao_destino'] = forms.IntegerField(required=False, widget=forms.HiddenInput())
        self.fields['grande_comando_destino'] = forms.IntegerField(required=False, widget=forms.HiddenInput())
        self.fields['unidade_destino'] = forms.IntegerField(required=False, widget=forms.HiddenInput())
        self.fields['sub_unidade_destino'] = forms.IntegerField(required=False, widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = super().clean()
        organograma_destino = cleaned_data.get('organograma_destino')
        
        # Validar se foi selecionada uma organização de destino
        if not organograma_destino:
            raise forms.ValidationError('É necessário selecionar uma organização de destino.')
        
        # Validar se a organização de destino não é a mesma da origem
        if self.viatura:
            origem_sub = self.viatura.sub_unidade
            origem_unidade = self.viatura.unidade
            origem_gc = self.viatura.grande_comando
            origem_orgao = self.viatura.orgao
            
            destino_sub = cleaned_data.get('sub_unidade_destino')
            destino_unidade = cleaned_data.get('unidade_destino')
            destino_gc = cleaned_data.get('grande_comando_destino')
            destino_orgao = cleaned_data.get('orgao_destino')
            
            # Verificar se é a mesma organização
            # Comparar IDs corretamente
            if (origem_sub and destino_sub and origem_sub.id == int(destino_sub)) or \
               (origem_unidade and destino_unidade and origem_unidade.id == int(destino_unidade)) or \
               (origem_gc and destino_gc and origem_gc.id == int(destino_gc)) or \
               (origem_orgao and destino_orgao and origem_orgao.id == int(destino_orgao)):
                raise forms.ValidationError('A organização de destino deve ser diferente da organização de origem.')
        
        return cleaned_data
    
    def clean_valor_aquisicao(self):
        """Converte valor formatado em BRL para formato numérico"""
        valor = self.cleaned_data.get('valor_aquisicao', '')
        
        if not valor or valor == '':
            return None
        
        # Se já for uma string numérica, tentar converter
        if isinstance(valor, str):
            # Remover formatação brasileira (pontos de milhar e vírgula decimal)
            valor_limpo = valor.replace('R$', '').replace(' ', '').strip()
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
            
            try:
                return float(valor_limpo)
            except (ValueError, TypeError):
                return None
        
        return valor


class AbastecimentoViaturaForm(forms.ModelForm):
    """Formulário para cadastro e edição de abastecimentos de viaturas"""
    
    class Meta:
        from .models import AbastecimentoViatura
        model = AbastecimentoViatura
        fields = [
            'viatura', 'data_abastecimento', 'quantidade_litros', 'valor_litro', 
            'valor_total', 'km_abastecimento', 'tipo_combustivel', 'posto_fornecedor',
            'com_aditivos', 'tipo_aditivo', 'quantidade_aditivo', 'valor_unitario_aditivo',
            'valor_total_aditivo', 'valor_total_nota', 'responsavel', 'observacoes', 'ativo'
        ]
        widgets = {
            'viatura': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'data_abastecimento': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'id': 'id_data_abastecimento'
            }),
            'quantidade_litros': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Ex: 50.00'
            }),
            'valor_litro': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_litro',
                'placeholder': 'Digite o valor',
                'type': 'text'
            }),
            'valor_total': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_total',
                'placeholder': 'Será calculado automaticamente',
                'readonly': True,
                'type': 'text'
            }),
            'km_abastecimento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'KM no momento do abastecimento'
            }),
            'tipo_combustivel': forms.Select(attrs={'class': 'form-select'}),
            'posto_fornecedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do posto ou fornecedor'
            }),
            'com_aditivos': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_com_aditivos',
            }),
            'tipo_aditivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Aditivo para diesel, limpa bicos, etc.',
                'id': 'id_tipo_aditivo',
            }),
            'quantidade_aditivo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Quantidade',
                'id': 'id_quantidade_aditivo',
            }),
            'valor_unitario_aditivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Valor unitário',
                'type': 'text',
                'id': 'id_valor_unitario_aditivo',
            }),
            'valor_total_aditivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calculado automaticamente',
                'readonly': True,
                'type': 'text',
                'id': 'id_valor_total_aditivo',
            }),
            'valor_total_nota': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Soma automática',
                'readonly': True,
                'type': 'text',
                'id': 'id_valor_total_nota',
            }),
            'responsavel': forms.Select(attrs={
                'class': 'form-select militar-select2',
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre o abastecimento...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Viatura, Militar
        
        # Filtrar apenas viaturas ativas
        self.fields['viatura'].queryset = Viatura.objects.filter(ativo=True).order_by('placa')
        
        # Filtrar apenas militares ativos e ordenar por posto e nome
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        from django.db.models import Case, When, Value, IntegerField
        hierarquia_ordem = Case(
            *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        militares_queryset = Militar.objects.filter(
            classificacao='ATIVO'
        ).annotate(
            ordem_hierarquia=hierarquia_ordem
        ).order_by(
            'ordem_hierarquia',
            'nome_completo'
        )
        self.fields['responsavel'].queryset = militares_queryset
        
        # Personalizar labels das opções para mostrar posto + nome
        self.fields['responsavel'].label_from_instance = lambda obj: f"{obj.get_posto_graduacao_display()} {obj.nome_completo}"
        
        # Configurar data/hora padrão
        if 'data_abastecimento' in self.fields:
            from django.utils import timezone
            if not self.instance.pk:
                # Novo abastecimento: usar data/hora atual
                self.fields['data_abastecimento'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')
            else:
                # Edição: usar data/hora do registro
                if self.instance.data_abastecimento:
                    self.fields['data_abastecimento'].initial = self.instance.data_abastecimento.strftime('%Y-%m-%dT%H:%M')
        
        # Se houver uma viatura selecionada, usar o KM atual como sugestão
        viatura_id = self.request.GET.get('viatura') if hasattr(self, 'request') and self.request else None
        if viatura_id:
            try:
                viatura_obj = Viatura.objects.get(pk=viatura_id)
                self.fields['viatura'].initial = viatura_obj
                if 'km_abastecimento' in self.fields and not self.initial.get('km_abastecimento'):
                    self.fields['km_abastecimento'].initial = viatura_obj.km_atual
            except Viatura.DoesNotExist:
                pass
        
        if self.instance and self.instance.pk and self.instance.viatura:
            if 'km_abastecimento' in self.fields and not self.initial.get('km_abastecimento'):
                self.initial['km_abastecimento'] = self.instance.viatura.km_atual
        elif self.initial.get('viatura'):
            try:
                viatura = Viatura.objects.get(pk=self.initial['viatura'])
                if 'km_abastecimento' in self.fields:
                    self.initial['km_abastecimento'] = viatura.km_atual
            except:
                pass
    
    def clean_valor_litro(self):
        """Converte valor formatado em BRL para formato numérico"""
        valor = self.cleaned_data.get('valor_litro', '')
        
        if not valor or valor == '':
            raise forms.ValidationError("Este campo é obrigatório.")
        
        if isinstance(valor, str):
            valor_limpo = valor.replace('R$', '').replace(' ', '').strip()
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
            
            try:
                return float(valor_limpo)
            except (ValueError, TypeError):
                raise forms.ValidationError("Valor inválido. Use o formato: 5,50 ou 5.50")
        
        return valor
    
    def clean_valor_total(self):
        """Converte valor formatado em BRL para formato numérico"""
        valor = self.cleaned_data.get('valor_total', '')
        
        if not valor or valor == '':
            return None
        
        if isinstance(valor, str):
            valor_limpo = valor.replace('R$', '').replace(' ', '').strip()
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
            
            try:
                return float(valor_limpo)
            except (ValueError, TypeError):
                return None
        
        return valor
    
    def clean(self):
        """Validações customizadas"""
        cleaned_data = super().clean()
        quantidade_litros = cleaned_data.get('quantidade_litros')
        valor_litro = cleaned_data.get('valor_litro')
        valor_total = cleaned_data.get('valor_total')
        viatura = cleaned_data.get('viatura')
        km_abastecimento = cleaned_data.get('km_abastecimento')
        
        # Calcular valor total se não fornecido
        if quantidade_litros and valor_litro:
            valor_calculado = quantidade_litros * valor_litro
            if not valor_total:
                cleaned_data['valor_total'] = valor_calculado
            elif abs(float(valor_total) - float(valor_calculado)) > 0.01:
                raise forms.ValidationError(
                    f"O valor total deve ser igual a quantidade × valor por litro (R$ {valor_calculado:.2f})."
                )
        
        # Validar KM (não pode ser menor que o último abastecimento)
        if viatura and km_abastecimento:
            from .models import AbastecimentoViatura
            from django.utils import timezone
            
            abastecimentos_anteriores = AbastecimentoViatura.objects.filter(
                viatura=viatura
            ).exclude(pk=self.instance.pk if self.instance.pk else None).order_by('-data_abastecimento', '-km_abastecimento')
            
            if abastecimentos_anteriores.exists():
                km_anterior = abastecimentos_anteriores.first().km_abastecimento
                if km_abastecimento < km_anterior:
                    raise forms.ValidationError(
                        f"O KM do abastecimento ({km_abastecimento}) não pode ser menor que o KM do último abastecimento registrado ({km_anterior})."
                    )
        
        return cleaned_data


class ManutencaoViaturaForm(forms.ModelForm):
    """Formulário para cadastro e edição de manutenções de viaturas"""
    
    class Meta:
        from .models import ManutencaoViatura
        model = ManutencaoViatura
        fields = [
            'viatura', 'data_manutencao', 'tipo_manutencao', 'km_manutencao', 
            'descricao_servico', 'fornecedor_oficina', 'valor_manutencao', 
            'pecas_trocadas', 'proximo_km_revisao', 'responsavel', 'observacoes', 'ativo'
        ]
        widgets = {
            'viatura': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'data_manutencao': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'id': 'id_data_manutencao'
            }),
            'tipo_manutencao': forms.Select(attrs={'class': 'form-select'}),
            'km_manutencao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'KM no momento da manutenção'
            }),
            'descricao_servico': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva os serviços realizados...'
            }),
            'fornecedor_oficina': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da oficina'
            }),
            'valor_manutencao': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_manutencao',
                'placeholder': 'Digite o valor',
                'type': 'text'
            }),
            'pecas_trocadas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lista de peças que foram substituídas...'
            }),
            'proximo_km_revisao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'KM previsto para a próxima revisão',
                'id': 'id_proximo_km_revisao'
            }),
            'responsavel': forms.Select(attrs={
                'class': 'form-select militar-select2',
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a manutenção...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Viatura, Militar
        
        # Filtrar apenas viaturas ativas
        self.fields['viatura'].queryset = Viatura.objects.filter(ativo=True).order_by('placa')
        
        # Filtrar apenas militares ativos e ordenar por posto e nome
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        from django.db.models import Case, When, Value, IntegerField
        hierarquia_ordem = Case(
            *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        militares_queryset = Militar.objects.filter(
            classificacao='ATIVO'
        ).annotate(
            ordem_hierarquia=hierarquia_ordem
        ).order_by(
            'ordem_hierarquia',
            'nome_completo'
        )
        self.fields['responsavel'].queryset = militares_queryset
        
        # Personalizar labels das opções para mostrar posto + nome
        self.fields['responsavel'].label_from_instance = lambda obj: f"{obj.get_posto_graduacao_display()} {obj.nome_completo}"
    
    def clean_valor_manutencao(self):
        """Converte valor formatado em BRL para formato numérico"""
        valor = self.cleaned_data.get('valor_manutencao', '')
        
        if not valor or valor == '':
            raise forms.ValidationError('O valor da manutenção é obrigatório.')
        
        # Se já for uma string numérica, tentar converter
        if isinstance(valor, str):
            # Remover formatação brasileira (pontos de milhar e vírgula decimal)
            valor_limpo = valor.replace('R$', '').replace(' ', '').strip()
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
            
            try:
                return float(valor_limpo)
            except (ValueError, TypeError):
                raise forms.ValidationError('Valor inválido. Use números e vírgula para decimais.')
        
        return valor
    
    def clean(self):
        """Validações adicionais"""
        cleaned_data = super().clean()
        km_manutencao = cleaned_data.get('km_manutencao')
        viatura = cleaned_data.get('viatura')
        
        # Validar que KM não seja menor que o anterior (se houver)
        if viatura and km_manutencao:
            from .models import ManutencaoViatura
            manutencoes_anteriores = ManutencaoViatura.objects.filter(
                viatura=viatura,
                ativo=True
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if manutencoes_anteriores.exists():
                km_anterior = manutencoes_anteriores.order_by('-data_manutencao', '-km_manutencao').first().km_manutencao
                if km_manutencao < km_anterior:
                    raise forms.ValidationError(
                        f"O KM da manutenção ({km_manutencao}) não pode ser menor que o KM da última manutenção registrada ({km_anterior})."
                    )
        
        return cleaned_data


class RodagemViaturaForm(forms.ModelForm):
    """Formulário para cadastro e edição de rodagens de viaturas"""
    
    class Meta:
        from .models import RodagemViatura
        model = RodagemViatura
        fields = [
            'viatura', 'condutor', 'data_saida', 'hora_saida', 'data_retorno', 'hora_retorno',
            'km_inicial', 'km_final', 'objetivo', 'destino', 
            'observacoes', 'status', 'ativo'
        ]
        widgets = {
            'viatura': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'condutor': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'data_saida': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'id': 'id_data_saida'
                },
                format='%Y-%m-%d'
            ),
            'hora_saida': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'id': 'id_hora_saida'
                },
                format='%H:%M'
            ),
            'data_retorno': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'id': 'id_data_retorno'
                },
                format='%Y-%m-%d'
            ),
            'hora_retorno': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'id': 'id_hora_retorno'
                },
                format='%H:%M'
            ),
            'km_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'KM no momento da saída'
            }),
            'km_final': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'KM no momento do retorno'
            }),
            'objetivo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'destino': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local de destino da viatura'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a rodagem...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair request do kwargs ANTES de chamar super (ModelForm não aceita 'request')
        self.request = kwargs.pop('request', None)
        
        super().__init__(*args, **kwargs)
        from .models import Viatura, Militar
        
        # Filtrar apenas viaturas ativas
        self.fields['viatura'].queryset = Viatura.objects.filter(ativo=True).order_by('placa')

        # Condutor obrigatório e apenas militares ativos
        if 'condutor' in self.fields:
            self.fields['condutor'].required = True
            try:
                self.fields['condutor'].queryset = Militar.objects.filter(classificacao='ATIVO').order_by('nome_completo')
            except Exception:
                pass
        
        # Se for edição (tem instância com PK), garantir formatação correta dos widgets
        if self.instance and self.instance.pk:
            # Na edição, o Django já preenche automaticamente os campos com os valores da instância
            # Mas precisamos garantir que os widgets de data/hora formatem corretamente
            
            # Configurar formato dos widgets de data
            if 'data_saida' in self.fields and self.instance.data_saida:
                self.fields['data_saida'].widget.format = '%Y-%m-%d'
            if 'data_retorno' in self.fields and self.instance.data_retorno:
                self.fields['data_retorno'].widget.format = '%Y-%m-%d'
            
            # Configurar formato dos widgets de hora
            if 'hora_saida' in self.fields and self.instance.hora_saida:
                self.fields['hora_saida'].widget.format = '%H:%M'
            if 'hora_retorno' in self.fields and self.instance.hora_retorno:
                self.fields['hora_retorno'].widget.format = '%H:%M'
            
            # Não modificar nenhum outro valor - deixar o Django usar os valores da instância
            return
        
        # Se for uma nova rodagem (não edição), calcular KM inicial automaticamente
        # Nova rodagem: verificar se há rodagens anteriores
        viatura_id = None
        
        # Tentar obter viatura de várias fontes (em ordem de prioridade)
        # 1. Do GET (se veio da URL)
        if hasattr(self, 'request') and self.request:
            viatura_id = self.request.GET.get('viatura')
        
        # 2. Do POST (se formulário foi submetido)
        if not viatura_id and hasattr(self, 'data') and self.data:
            viatura_id = self.data.get('viatura')
        
        # 3. Do initial (valores iniciais passados) - pode vir como objeto ou ID
        if not viatura_id and self.initial.get('viatura'):
            viatura_selecionada = self.initial.get('viatura')
            if hasattr(viatura_selecionada, 'pk'):
                viatura_id = viatura_selecionada.pk
            elif isinstance(viatura_selecionada, (int, str)):
                viatura_id = viatura_selecionada
        
        if viatura_id:
            try:
                from .models import RodagemViatura
                viatura_obj = Viatura.objects.get(pk=viatura_id)
                
                # Só definir initial se não houver valor já definido
                if not self.initial.get('viatura'):
                    self.fields['viatura'].initial = viatura_obj
                
                # Buscar a última rodagem finalizada desta viatura
                ultima_rodagem = RodagemViatura.objects.filter(
                    viatura=viatura_obj,
                    status='FINALIZADA',
                    ativo=True
                ).order_by('-data_retorno', '-hora_retorno', '-data_saida', '-hora_saida').first()
                
                # Se houver última rodagem com KM final, usar esse valor
                # IMPORTANTE: Não usar km_atual da viatura para manter independência do controle de combustível
                if ultima_rodagem and ultima_rodagem.km_final:
                    km_sugerido = ultima_rodagem.km_final
                else:
                    # Se não houver rodagens anteriores, não sugerir KM (deixar vazio)
                    km_sugerido = None
                
                # Definir o KM inicial apenas se houver sugestão e o campo estiver vazio
                if km_sugerido and 'km_inicial' in self.fields:
                    # Verificar se já não há valor inicial
                    if not self.initial.get('km_inicial'):
                        self.fields['km_inicial'].initial = km_sugerido
                    
            except (Viatura.DoesNotExist, ValueError, TypeError):
                pass
        
        # Configurar data/hora padrão para saída (apenas para nova rodagem)
        if 'data_saida' in self.fields:
            from django.utils import timezone
            # Usar data atual apenas se não houver valor inicial ou no POST
            tem_valor = (
                self.initial.get('data_saida') or 
                (hasattr(self, 'data') and self.data.get('data_saida'))
            )
            if not tem_valor:
                self.fields['data_saida'].initial = timezone.now().date()
        
        if 'hora_saida' in self.fields:
            from django.utils import timezone
            import pytz
            # Usar hora atual de Brasília apenas se não houver valor inicial ou no POST
            tem_valor = (
                self.initial.get('hora_saida') or 
                (hasattr(self, 'data') and self.data.get('hora_saida'))
            )
            if not tem_valor:
                brasilia_tz = pytz.timezone('America/Sao_Paulo')
                agora_brasilia = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
                self.fields['hora_saida'].initial = agora_brasilia.time()
        
        # Condutor padrão: militar do usuário (se disponível)
        if 'condutor' in self.fields and self.request and hasattr(self.request.user, 'militar') and self.request.user.militar:
            self.fields['condutor'].initial = self.request.user.militar
    
    def clean(self):
        """Validações customizadas"""
        cleaned_data = super().clean()
        km_inicial = cleaned_data.get('km_inicial')
        km_final = cleaned_data.get('km_final')
        viatura = cleaned_data.get('viatura')
        data_saida = cleaned_data.get('data_saida')
        hora_saida = cleaned_data.get('hora_saida')
        data_retorno = cleaned_data.get('data_retorno')
        hora_retorno = cleaned_data.get('hora_retorno')
        
        # Validação removida: KM inicial não precisa ser validado contra km_atual da viatura
        # pois o controle de rodagem é independente do controle de combustível
        
        # Validar que KM final seja maior ou igual ao KM inicial (se houver)
        if km_final and km_inicial:
            if km_final < km_inicial:
                raise forms.ValidationError(
                    f"O KM final ({km_final}) não pode ser menor que o KM inicial ({km_inicial})."
                )
        
        # Validar que se tiver data/hora de retorno, deve ter data/hora de saída
        if data_retorno and not data_saida:
            raise forms.ValidationError("Se houver data de retorno, deve haver data de saída.")
        
        if hora_retorno and not hora_saida:
            raise forms.ValidationError("Se houver hora de retorno, deve haver hora de saída.")
        
        # Validar que data de retorno não seja anterior à data de saída
        if data_retorno and data_saida:
            if data_retorno < data_saida:
                raise forms.ValidationError("A data de retorno não pode ser anterior à data de saída.")
            
            # Se for no mesmo dia, validar hora
            if data_retorno == data_saida and hora_retorno and hora_saida:
                from datetime import datetime, date, time
                hora_saida_dt = datetime.combine(date.today(), hora_saida)
                hora_retorno_dt = datetime.combine(date.today(), hora_retorno)
                if hora_retorno_dt < hora_saida_dt:
                    raise forms.ValidationError("A hora de retorno não pode ser anterior à hora de saída no mesmo dia.")
        
        return cleaned_data


class LicencaEspecialForm(forms.ModelForm):
    """Formulário para gerenciar licenças especiais dos militares"""
    
    class Meta:
        from .models import LicencaEspecial
        model = LicencaEspecial
        fields = [
            'militar', 'decenio', 'quantidade_meses', 'data_inicio', 'data_fim',
            'status', 'observacoes', 'documento_referencia', 'numero_documento'
        ]
        widgets = {
            'militar': forms.Select(attrs={
                'class': 'form-select militar-select2',
                'data-placeholder': 'Digite o nome, matrícula ou posto do militar...',
                'style': 'width: 100%'
            }),
            'decenio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'placeholder': 'Ex: 1 para 1º decênio, 2 para 2º decênio, etc.',
                'onchange': 'mostrarPeriodoDecenio()',
                'id': 'id_decenio'
            }),
            'quantidade_meses': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 12,
                'onchange': 'calcularDataFimLicenca()',
                'id': 'id_quantidade_meses'
            }),
            'data_inicio': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'onchange': 'calcularDataFimLicenca()',
                    'id': 'id_data_inicio'
                }
            ),
            'data_fim': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'readonly': True,
                    'id': 'id_data_fim'
                }
            ),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais...'
            }),
            'documento_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria, Decreto, etc.'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: DOE n° 001/2025 de 25/01/2025'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tornar o campo militar obrigatório apenas na criação
        if not self.instance.pk:
            self.fields['militar'].required = True
            # Ordenar militares por hierarquia (posto) e depois por antiguidade
            ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
            from django.db.models import Case, When, Value, IntegerField
            hierarquia_ordem = Case(
                *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
                default=Value(len(ordem_hierarquica)),
                output_field=IntegerField()
            )
            # Incluir todos os militares ativos no queryset para validação
            self.fields['militar'].queryset = Militar.objects.filter(
                classificacao='ATIVO'
            ).annotate(
                ordem_hierarquia=hierarquia_ordem
            ).order_by(
                'ordem_hierarquia',
                'data_promocao_atual',
                'numeracao_antiguidade',
                'nome_completo'
            )
        else:
            self.fields['militar'].required = False
            # Se está editando, incluir o militar atual no queryset
            if self.instance.militar:
                # Ordenar militares por hierarquia (posto) e depois por antiguidade
                ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
                from django.db.models import Case, When, Value, IntegerField, Q
                hierarquia_ordem = Case(
                    *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
                    default=Value(len(ordem_hierarquica)),
                    output_field=IntegerField()
                )
                # Incluir o militar atual e todos os ativos no queryset para validação
                self.fields['militar'].queryset = Militar.objects.filter(
                    Q(id=self.instance.militar.id) | Q(classificacao='ATIVO')
                ).annotate(
                    ordem_hierarquia=hierarquia_ordem
                ).order_by(
                    'ordem_hierarquia',
                    'data_promocao_atual',
                    'numeracao_antiguidade',
                    'nome_completo'
                )
        
        # Tornar data_fim readonly pois será calculado automaticamente
        self.fields['data_fim'].widget.attrs['readonly'] = True
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        quantidade_meses = cleaned_data.get('quantidade_meses')
        
        # Calcular data_fim se não fornecida
        if data_inicio and quantidade_meses:
            from dateutil.relativedelta import relativedelta
            data_fim_calculada = data_inicio + relativedelta(months=quantidade_meses, days=-1)
            cleaned_data['data_fim'] = data_fim_calculada
        
        # Validar decênio baseado no tempo de serviço do militar
        militar = cleaned_data.get('militar')
        decenio = cleaned_data.get('decenio')
        data_inicio = cleaned_data.get('data_inicio')
        
        if militar and militar.data_ingresso and decenio:
            from datetime import date
            hoje = date.today()
            anos_de_servico = hoje.year - militar.data_ingresso.year
            if (hoje.month, hoje.day) < (militar.data_ingresso.month, militar.data_ingresso.day):
                anos_de_servico -= 1
            
            decenio_maximo = (anos_de_servico // 10) + 1
            if decenio > decenio_maximo:
                raise forms.ValidationError({
                    'decenio': f'O decênio informado ({decenio}º) é maior que o possível com base no tempo de serviço do militar ({anos_de_servico} anos). Máximo: {decenio_maximo}º decênio.'
                })
            
            # Validar que a data de início deve ser posterior à data de conclusão do decênio
            if data_inicio:
                anos_fim = decenio * 10
                data_fim_decenio = date(
                    militar.data_ingresso.year + anos_fim,
                    militar.data_ingresso.month,
                    militar.data_ingresso.day
                )
                
                if data_inicio <= data_fim_decenio:
                    raise forms.ValidationError({
                        'data_inicio': (
                            f'A data de início da licença especial deve ser posterior à data de conclusão do decênio. '
                            f'O {decenio}º decênio será completado em {data_fim_decenio.strftime("%d/%m/%Y")}. '
                            f'A data de início deve ser após esta data.'
                        )
                    })
            
            # Validar que a soma das licenças especiais do mesmo decênio não pode ultrapassar 6 meses
            quantidade_meses = cleaned_data.get('quantidade_meses')
            if quantidade_meses:
                if self.instance.pk:
                    # Se estiver editando, excluir a própria licença
                    licencas_mesmo_decenio = militar.licencas_especiais.filter(
                        decenio=decenio
                    ).exclude(status='CANCELADA').exclude(pk=self.instance.pk)
                else:
                    # Se for criação, verificar todas as licenças do mesmo decênio
                    licencas_mesmo_decenio = militar.licencas_especiais.filter(
                        decenio=decenio
                    ).exclude(status='CANCELADA')
                
                # Calcular total de meses já cadastrados para este decênio
                total_meses_decenio = sum(licenca.quantidade_meses for licenca in licencas_mesmo_decenio)
                
                # Adicionar os meses da licença atual
                total_meses_com_esta = total_meses_decenio + quantidade_meses
                
                # Validar que não pode ultrapassar 6 meses
                if total_meses_com_esta > 6:
                    meses_restantes = 6 - total_meses_decenio
                    raise forms.ValidationError({
                        'quantidade_meses': (
                            f'A soma das licenças especiais do {decenio}º decênio não pode ultrapassar 6 meses. '
                            f'Já existem {total_meses_decenio} mês{"es" if total_meses_decenio != 1 else ""} cadastrado{"s" if total_meses_decenio != 1 else ""} para este decênio. '
                            f'Você pode cadastrar no máximo {meses_restantes} mês{"es" if meses_restantes != 1 else ""} adicional{"is" if meses_restantes != 1 else ""}.'
                        )
                    })
            
            # Validação de sequência removida - permite cadastrar qualquer decênio
        
        # Verificar choque de datas com outros afastamentos
        if militar and data_inicio:
            data_fim = cleaned_data.get('data_fim')
            if data_fim:
                choques = verificar_choque_datas_afastamentos(militar, data_inicio, data_fim, instance=self.instance)
                if choques:
                    mensagem = "<strong>⚠️ ATENÇÃO: Há choque de datas com os seguintes afastamentos:</strong><br><br>"
                    mensagem += "<ul style='margin-bottom: 0;'>"
                    mensagem += "".join(f"<li>{choque}</li>" for choque in choques)
                    mensagem += "</ul><br>"
                    mensagem += "<strong>Por favor, ajuste as datas para evitar o choque ou cancele os afastamentos conflitantes.</strong>"
                    raise forms.ValidationError(mensagem)
        
        return cleaned_data


class PlanoLicencaEspecialForm(forms.ModelForm):
    """Formulário para gerenciar planos de licenças especiais"""
    
    class Meta:
        from .models import PlanoLicencaEspecial
        model = PlanoLicencaEspecial
        fields = [
            'ano_plano', 'titulo', 'descricao', 'status',
            'documento_referencia', 'numero_documento'
        ]
        widgets = {
            'ano_plano': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000,
                'max': 2100
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Plano de Licenças Especiais 2025'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição do plano de licenças especiais...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'documento_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria, Decreto, etc.'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do documento'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from datetime import datetime
        ano_atual = datetime.now().year
        
        # Se for edição (já tem pk), remover o campo status do formulário
        if self.instance.pk:
            # Remover o campo status da edição - status só pode ser alterado pela aprovação
            if 'status' in self.fields:
                del self.fields['status']
        
        # Definir valores padrão para criação
        if not self.instance.pk:
            if not self.initial.get('ano_plano'):
                self.initial['ano_plano'] = ano_atual
            if not self.initial.get('titulo'):
                self.initial['titulo'] = f'Plano de Licenças Especiais {ano_atual}'
    
    def clean(self):
        cleaned_data = super().clean()
        ano_plano = cleaned_data.get('ano_plano')
        
        if ano_plano and (ano_plano <= 2000 or ano_plano > 2100):
            raise forms.ValidationError({
                'ano_plano': 'Ano do plano deve estar entre 2000 e 2100.'
            })
        
        return cleaned_data


class ArmaForm(forms.ModelForm):
    """Formulário para cadastro e edição de armas da instituição"""
    
    # Campo para seleção hierárquica do organograma (não é salvo diretamente)
    organograma_select = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'organograma-select'
        })
    )
    
    # Campo para seleção de configuração de arma (não é salvo diretamente)
    configuracao_arma = forms.ModelChoiceField(
        queryset=ConfiguracaoArma.objects.filter(ativo=True).order_by('marca', 'modelo'),
        required=False,
        empty_label='Selecione uma configuração de arma (opcional)',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'configuracao-arma-select'
        }),
        label='Configuração de Arma',
        help_text='Selecione uma configuração para preencher automaticamente tipo, calibre, marca e modelo'
    )
    
    class Meta:
        model = Arma
        fields = [
            'numero_serie', 'nome_tombamento', 'numero_tombamento', 'cod_tombamento', 'local_tombamento',
            'tipo', 'marca', 'modelo', 'calibre', 'alma_raiada', 'quantidade_raias', 'direcao_raias',
            'capacidade_carregador', 'situacao', 'estado_conservacao', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'numero_inquerito_pm', 'encarregado_inquerito_pm', 'numero_inquerito_pc', 'delegado_inquerito_pc',
            'numero_registro_policia', 'numero_guia_transito', 'data_aquisicao', 'fornecedor', 'valor_aquisicao',
            'observacoes', 'ativo'
        ]
        widgets = {
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de série da arma',
                'style': 'text-transform: uppercase;'
            }),
            'nome_tombamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PISTOLA BERETTA APX FULL SICE CAL. 9X19MM + MALETA + 4 CARREGADORES'
            }),
            'numero_tombamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 321-02-90'
            }),
            'cod_tombamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 163978'
            }),
            'local_tombamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: BM-4'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Taurus, Glock, IMBEL'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PT 100, G17, FAL'
            }),
            'calibre': forms.Select(attrs={'class': 'form-select'}),
            'alma_raiada': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_alma_raiada'}),
            'quantidade_raias': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'id': 'id_quantidade_raias',
                'placeholder': 'Ex: 4, 6, 8'
            }),
            'direcao_raias': forms.Select(attrs={'class': 'form-select', 'id': 'id_direcao_raias'}),
            'capacidade_carregador': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Quantidade de munições'
            }),
            'situacao': forms.Select(attrs={'class': 'form-select', 'id': 'id_situacao'}),
            'estado_conservacao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_estado_conservacao'
            }),
            'orgao': forms.Select(attrs={'class': 'form-select'}),
            'numero_inquerito_pm': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_numero_inquerito_pm',
                'placeholder': 'Número do inquérito PM'
            }),
            'encarregado_inquerito_pm': forms.Select(attrs={'class': 'form-select', 'id': 'id_encarregado_inquerito_pm'}),
            'numero_inquerito_pc': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_numero_inquerito_pc',
                'placeholder': 'Número do inquérito PC'
            }),
            'delegado_inquerito_pc': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_delegado_inquerito_pc',
                'placeholder': 'Nome do delegado responsável'
            }),
            'numero_registro_policia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nº Registro no Exército Brasileiro'
            }),
            'numero_guia_transito': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nº Guia de Trânsito'
            }),
            'data_aquisicao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fornecedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fornecedor da arma'
            }),
            'valor_aquisicao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações sobre a arma...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Reordenar campos para colocar configuracao_arma no início
        field_order = ['configuracao_arma', 'numero_serie', 'tipo', 'marca', 'modelo', 'calibre']
        remaining_fields = [f for f in self.fields.keys() if f not in field_order]
        self.fields = {f: self.fields[f] for f in field_order + remaining_fields}


class ArmaParticularForm(forms.ModelForm):
    """Formulário para cadastro e edição de armas particulares"""
    
    class Meta:
        model = ArmaParticular
        fields = [
            'militar', 'numero_serie', 'tipo', 'marca', 'modelo', 'calibre', 'alma_raiada', 'quantidade_raias', 'direcao_raias', 'numero_canhao',
            'capacidade_carregador', 'status', 'numero_registro_policia', 'data_validade_registro',
            'numero_guia_transito', 'data_validade_guia', 'autorizado_uso_servico',
            'data_autorizacao', 'data_vencimento_autorizacao', 'observacoes', 'ativo'
        ]
        widgets = {
            'militar': forms.Select(attrs={'class': 'form-select militar-select2'}),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de série da arma',
                'style': 'text-transform: uppercase;'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Taurus, Glock, IMBEL'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PT 100, G17, FAL'
            }),
            'calibre': forms.Select(attrs={'class': 'form-select'}),
            'alma_raiada': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_alma_raiada'}),
            'quantidade_raias': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'id': 'id_quantidade_raias',
                'placeholder': 'Ex: 4, 6, 8'
            }),
            'direcao_raias': forms.Select(attrs={'class': 'form-select', 'id': 'id_direcao_raias'}),
            'numero_canhao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do canhão (se aplicável)'
            }),
            'capacidade_carregador': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Quantidade de munições'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'numero_registro_policia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nº Registro SIGMA'
            }),
            'data_validade_registro': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'numero_guia_transito': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nº Guia de Trânsito'
            }),
            'data_validade_guia': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'autorizado_uso_servico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'data_autorizacao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'data_vencimento_autorizacao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações sobre a arma...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Permitir qualquer militar (o Select2 vai fazer a busca e validação via AJAX)
        # Não limitar o queryset aqui para permitir que o Select2 funcione corretamente
        self.fields['militar'].queryset = Militar.objects.all().order_by('nome_completo')
        
        # Garantir que as datas sejam formatadas corretamente para inputs do tipo date
        if self.instance and self.instance.pk:
            if self.instance.data_validade_registro:
                self.initial['data_validade_registro'] = self.instance.data_validade_registro.strftime('%Y-%m-%d')
            if self.instance.data_validade_guia:
                self.initial['data_validade_guia'] = self.instance.data_validade_guia.strftime('%Y-%m-%d')
            if self.instance.data_autorizacao:
                self.initial['data_autorizacao'] = self.instance.data_autorizacao.strftime('%Y-%m-%d')
            if self.instance.data_vencimento_autorizacao:
                self.initial['data_vencimento_autorizacao'] = self.instance.data_vencimento_autorizacao.strftime('%Y-%m-%d')


class TransferenciaArmaForm(forms.Form):
    """Formulário para transferência de armas entre organizações"""
    
    # Campo para seleção hierárquica do organograma de origem
    organograma_origem = forms.CharField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'organograma-origem-select'
        }),
        label='Organização de Origem'
    )
    
    # Campo para seleção hierárquica do organograma de destino
    organograma_destino = forms.CharField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'organograma-destino-select'
        }),
        label='Organização de Destino'
    )
    
    # Material acompanhando a arma
    quantidade_carregadores = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'id_quantidade_carregadores',
            'min': '0',
            'placeholder': 'Quantidade de carregadores'
        }),
        label='Quantidade de Carregadores',
        help_text='Quantidade de carregadores que acompanham a arma'
    )
    
    numeracao_carregadores = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'id_numeracao_carregadores',
            'rows': 3,
            'placeholder': 'Digite a numeração de cada carregador, separada por vírgula ou quebra de linha. Ex: 001, 002, 003'
        }),
        label='Numeração dos Carregadores',
        help_text='Digite a numeração de cada carregador, separada por vírgula ou quebra de linha.'
    )
    
    quantidade_municoes_catalogadas = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'id_quantidade_municoes_catalogadas',
            'min': '0',
            'placeholder': 'Quantidade de munições catalogadas'
        }),
        label='Quantidade de Munições Catalogadas',
        help_text='Quantidade de munições catalogadas que acompanham a arma'
    )
    
    justificativa = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Informe o motivo da transferência...'
        }),
        label='Justificativa',
        help_text='Motivo obrigatório para a transferência da arma'
    )
    
    observacoes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observações adicionais sobre a transferência...'
        }),
        label='Observações'
    )
    
    def __init__(self, *args, **kwargs):
        self.arma = kwargs.pop('arma', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        organograma_origem = cleaned_data.get('organograma_origem')
        organograma_destino = cleaned_data.get('organograma_destino')
        
        # Validar se foi selecionada uma organização de origem
        if not organograma_origem:
            raise forms.ValidationError('É necessário selecionar uma organização de origem.')
        
        # Validar se foi selecionada uma organização de destino
        if not organograma_destino:
            raise forms.ValidationError('É necessário selecionar uma organização de destino.')
        
        # Validar se a organização de destino não é a mesma da origem
        if organograma_origem == organograma_destino:
            raise forms.ValidationError('A organização de destino deve ser diferente da organização de origem.')
        
        return cleaned_data


class MovimentacaoArmaForm(forms.ModelForm):
    """Formulário para cadastro e edição de movimentações de armas (Entrega, Devolução, Manutenção)"""
    
    class Meta:
        model = MovimentacaoArma
        fields = [
            'arma', 'tipo_movimentacao', 'data_movimentacao', 'militar_origem',
            'militar_destino', 'organizacao_origem', 'organizacao_destino', 
            'quantidade_carregadores', 'numeracao_carregadores', 'quantidade_municoes_catalogadas', 'observacoes',
            'tipo_manutencao', 'orgao_manutencao', 'grande_comando_manutencao', 'unidade_manutencao', 
            'sub_unidade_manutencao', 'militar_recebeu_manutencao',
            'empresa_manutencao', 'cnpj_empresa_manutencao', 'endereco_empresa_manutencao', 'responsavel_empresa_manutencao',
            'motivos_manutencao', 'reparos_realizados'
        ]
        widgets = {
            'arma': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'tipo_movimentacao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_movimentacao'
            }),
            'data_movimentacao': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'id': 'id_data_movimentacao'
            }),
            'militar_origem': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_militar_origem'
            }),
            'militar_destino': forms.Select(attrs={
                'class': 'form-select militar-select2',
                'id': 'id_militar_destino'
            }),
            'organizacao_origem': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_organizacao_origem',
                'placeholder': 'Organização de origem',
                'readonly': True
            }),
            'organizacao_destino': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_organizacao_destino',
                'placeholder': 'Organização de destino',
                'readonly': True
            }),
            'quantidade_carregadores': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_quantidade_carregadores',
                'min': '0',
                'placeholder': 'Quantidade de carregadores'
            }),
            'numeracao_carregadores': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'id_numeracao_carregadores',
                'rows': 3,
                'placeholder': 'Digite a numeração de cada carregador, separada por vírgula ou quebra de linha. Ex: 001, 002, 003'
            }),
            'quantidade_municoes_catalogadas': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_quantidade_municoes_catalogadas',
                'min': '0',
                'placeholder': 'Quantidade de munições catalogadas'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações sobre a movimentação...'
            }),
            'tipo_manutencao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_manutencao'
            }),
            'orgao_manutencao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_orgao_manutencao'
            }),
            'grande_comando_manutencao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_grande_comando_manutencao'
            }),
            'unidade_manutencao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_unidade_manutencao'
            }),
            'sub_unidade_manutencao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_sub_unidade_manutencao'
            }),
            'militar_recebeu_manutencao': forms.Select(attrs={
                'class': 'form-select militar-select2',
                'id': 'id_militar_recebeu_manutencao'
            }),
            'empresa_manutencao': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_empresa_manutencao',
                'placeholder': 'Nome da empresa de manutenção'
            }),
            'cnpj_empresa_manutencao': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_cnpj_empresa_manutencao',
                'placeholder': 'XX.XXX.XXX/XXXX-XX',
                'data-mask': '00.000.000/0000-00'
            }),
            'endereco_empresa_manutencao': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'id_endereco_empresa_manutencao',
                'rows': 3,
                'placeholder': 'Endereço completo da empresa'
            }),
            'responsavel_empresa_manutencao': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_responsavel_empresa_manutencao',
                'placeholder': 'Nome do responsável na empresa'
            }),
            'motivos_manutencao': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'id_motivos_manutencao',
                'rows': 4,
                'placeholder': 'Descreva os motivos pelos quais a arma está sendo enviada para manutenção'
            }),
            'reparos_realizados': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'id_reparos_realizados',
                'rows': 4,
                'placeholder': 'Descreva os reparos realizados na arma durante a manutenção'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except Exception as e:
            import traceback
            print(f"Erro ao inicializar formulário base: {str(e)}")
            print(traceback.format_exc())
            raise
        
        # Configurar querysets para militares (apenas militares ativos)
        try:
            self.fields['militar_origem'].queryset = Militar.objects.filter(classificacao='ATIVO').order_by('nome_completo')
            self.fields['militar_origem'].required = False
            self.fields['militar_origem'].empty_label = 'Selecione um militar'
            
            self.fields['militar_destino'].queryset = Militar.objects.filter(classificacao='ATIVO').order_by('nome_completo')
            self.fields['militar_destino'].required = False
            self.fields['militar_destino'].empty_label = 'Selecione um militar'
        except Exception as e:
            import traceback
            print(f"Erro ao configurar querysets de militares: {str(e)}")
            print(traceback.format_exc())
            # Não levantar exceção, apenas logar o erro
        
        # Se for devolução e já tiver militar_origem preenchido, tornar readonly
        tipo_mov = None
        if hasattr(self, 'data') and self.data:
            tipo_mov = self.data.get('tipo_movimentacao')
        if not tipo_mov:
            # Tentar obter do initial (pode ser None ou um dict)
            initial = getattr(self, 'initial', None) or {}
            if isinstance(initial, dict):
                tipo_mov = initial.get('tipo_movimentacao')
        if not tipo_mov and self.instance and self.instance.pk:
            tipo_mov = self.instance.tipo_movimentacao
        
        # Verificar se é devolução e tem militar_origem
        initial = getattr(self, 'initial', None) or {}
        if isinstance(initial, dict) and tipo_mov == 'DEVOLUCAO' and initial.get('militar_origem'):
            # Tornar o campo readonly quando for devolução e já tiver valor
            self.fields['militar_origem'].widget.attrs['readonly'] = True
            self.fields['militar_origem'].widget.attrs['style'] = 'background-color: #f8f9fa; cursor: not-allowed;'
            # Não usar disabled pois campos disabled não são enviados no POST
            # O JavaScript vai desabilitar visualmente
        
        # Configurar queryset para armas (apenas armas ativas)
        self.fields['arma'].queryset = Arma.objects.filter(ativo=True).order_by('numero_serie')
        
        # Configurar querysets para campos de organograma de manutenção
        # Orgao, GrandeComando, Unidade, SubUnidade já estão importados no topo do arquivo
        try:
            if 'orgao_manutencao' in self.fields:
                self.fields['orgao_manutencao'].queryset = Orgao.objects.filter(ativo=True).order_by('nome')
                self.fields['orgao_manutencao'].required = False
                self.fields['orgao_manutencao'].empty_label = 'Selecione um órgão'
            if 'grande_comando_manutencao' in self.fields:
                self.fields['grande_comando_manutencao'].queryset = GrandeComando.objects.filter(ativo=True).order_by('nome')
                self.fields['grande_comando_manutencao'].required = False
                self.fields['grande_comando_manutencao'].empty_label = 'Selecione um grande comando'
            if 'unidade_manutencao' in self.fields:
                self.fields['unidade_manutencao'].queryset = Unidade.objects.filter(ativo=True).order_by('nome')
                self.fields['unidade_manutencao'].required = False
                self.fields['unidade_manutencao'].empty_label = 'Selecione uma unidade'
            if 'sub_unidade_manutencao' in self.fields:
                self.fields['sub_unidade_manutencao'].queryset = SubUnidade.objects.filter(ativo=True).order_by('nome')
                self.fields['sub_unidade_manutencao'].required = False
                self.fields['sub_unidade_manutencao'].empty_label = 'Selecione uma sub-unidade'
            if 'militar_recebeu_manutencao' in self.fields:
                self.fields['militar_recebeu_manutencao'].queryset = Militar.objects.filter(classificacao='ATIVO').order_by('nome_completo')
                self.fields['militar_recebeu_manutencao'].required = False
                self.fields['militar_recebeu_manutencao'].empty_label = 'Selecione um militar'
        except Exception as e:
            import traceback
            print(f"Erro ao configurar querysets de organograma: {str(e)}")
            print(traceback.format_exc())
            # Não levantar exceção, apenas logar o erro
        
        # Remover TRANSFERENCIA, ENTREGA e DEVOLUCAO das opções de tipo_movimentacao
        # Transferências têm formulário separado, Cautela/Descautela não são mais usadas
        if 'tipo_movimentacao' in self.fields:
            choices = list(self.fields['tipo_movimentacao'].choices)
            choices = [choice for choice in choices if choice[0] not in ['TRANSFERENCIA', 'ENTREGA', 'DEVOLUCAO']]
            self.fields['tipo_movimentacao'].choices = choices
        
        # Se for edição (tem instância com PK), preencher campos baseado na situação
        if self.instance and self.instance.pk:
            # Remover readonly dos campos para que apareçam no formulário de edição
            if 'organizacao_origem' in self.fields:
                if 'readonly' in self.fields['organizacao_origem'].widget.attrs:
                    self.fields['organizacao_origem'].widget.attrs.pop('readonly', None)
            if 'organizacao_destino' in self.fields:
                if 'readonly' in self.fields['organizacao_destino'].widget.attrs:
                    self.fields['organizacao_destino'].widget.attrs.pop('readonly', None)
    
    def clean(self):
        """Validação customizada baseada no tipo de movimentação"""
        cleaned_data = super().clean()
        tipo_mov = cleaned_data.get('tipo_movimentacao')
        arma = cleaned_data.get('arma')
        militar_destino = cleaned_data.get('militar_destino')
        
        # TRANSFERENCIA, ENTREGA e DEVOLUCAO não devem estar mais neste formulário
        if tipo_mov in ['TRANSFERENCIA', 'ENTREGA', 'DEVOLUCAO']:
            raise forms.ValidationError('Este tipo de movimentação não é mais suportado neste formulário.')
        
        # MANUTENCAO: validações específicas
        if tipo_mov == 'MANUTENCAO':
            # Validar se a arma está em RESERVA_ARMAMENTO
            if arma and arma.situacao != 'RESERVA_ARMAMENTO':
                raise forms.ValidationError({
                    'tipo_movimentacao': f'A arma deve estar em "Reserva de Armamento" para poder ser enviada para manutenção. Situação atual: {arma.get_situacao_display()}'
                })
            
            # Verificar se já existe manutenção em andamento
            if arma:
                # Buscar a última manutenção
                ultima_manutencao = arma.movimentacoes.filter(
                    tipo_movimentacao='MANUTENCAO'
                ).order_by('-data_movimentacao').first()
                
                if ultima_manutencao:
                    # Verificar se existe retorno para esta manutenção
                    retorno_existente = arma.movimentacoes.filter(
                        tipo_movimentacao='RETORNO_MANUTENCAO',
                        data_movimentacao__gt=ultima_manutencao.data_movimentacao
                    ).exists()
                    
                    if not retorno_existente:
                        # Existe manutenção sem retorno
                        manutencao_em_andamento = ultima_manutencao
                    else:
                        manutencao_em_andamento = None
                else:
                    manutencao_em_andamento = None
                
                if manutencao_em_andamento:
                    raise forms.ValidationError({
                        'tipo_movimentacao': f'A arma já está em manutenção desde {manutencao_em_andamento.data_movimentacao.strftime("%d/%m/%Y %H:%M")}. É necessário registrar o retorno antes de enviar para outra manutenção.'
                    })
            
            tipo_manutencao = cleaned_data.get('tipo_manutencao')
            if not tipo_manutencao:
                raise forms.ValidationError({
                    'tipo_manutencao': 'É necessário informar se a manutenção é Interna ou Externa.'
                })
            
            if tipo_manutencao == 'INTERNA':
                # Deve ter organograma ou militar que recebeu
                orgao_manutencao = cleaned_data.get('orgao_manutencao')
                grande_comando_manutencao = cleaned_data.get('grande_comando_manutencao')
                unidade_manutencao = cleaned_data.get('unidade_manutencao')
                sub_unidade_manutencao = cleaned_data.get('sub_unidade_manutencao')
                militar_recebeu = cleaned_data.get('militar_recebeu_manutencao')
                
                tem_organograma = orgao_manutencao or grande_comando_manutencao or unidade_manutencao or sub_unidade_manutencao
                
                if not tem_organograma and not militar_recebeu:
                    raise forms.ValidationError({
                        'militar_recebeu_manutencao': 'Para manutenção interna, é necessário informar a OM de destino ou o militar que recebeu a arma.'
                    })
            elif tipo_manutencao == 'EXTERNA':
                # Deve ter empresa e CNPJ
                if not cleaned_data.get('empresa_manutencao'):
                    raise forms.ValidationError({
                        'empresa_manutencao': 'Para manutenção externa, é necessário informar o nome da empresa.'
                    })
                if not cleaned_data.get('cnpj_empresa_manutencao'):
                    raise forms.ValidationError({
                        'cnpj_empresa_manutencao': 'Para manutenção externa, é necessário informar o CNPJ da empresa.'
                    })
        
        # RETORNO_MANUTENCAO: validar se a arma está em manutenção
        elif tipo_mov == 'RETORNO_MANUTENCAO':
            if arma and arma.situacao != 'EM_MANUTENCAO':
                raise forms.ValidationError({
                    'tipo_movimentacao': f'A arma deve estar em "Em Manutenção" para poder retornar. Situação atual: {arma.get_situacao_display()}'
                })
            
            if arma:
                # Verificar se existe uma manutenção sem retorno
                ultima_manutencao = arma.movimentacoes.filter(
                    tipo_movimentacao='MANUTENCAO'
                ).order_by('-data_movimentacao').first()
                
                if not ultima_manutencao:
                    raise forms.ValidationError({
                        'tipo_movimentacao': 'Não foi encontrada uma manutenção para esta arma.'
                    })
                
                # Verificar se já existe retorno para esta manutenção
                retorno_existente = arma.movimentacoes.filter(
                    tipo_movimentacao='RETORNO_MANUTENCAO',
                    data_movimentacao__gt=ultima_manutencao.data_movimentacao
                ).exists()
                
                if retorno_existente:
                    raise forms.ValidationError({
                        'tipo_movimentacao': f'A arma já retornou da manutenção iniciada em {ultima_manutencao.data_movimentacao.strftime("%d/%m/%Y %H:%M")}.'
                    })
        
        return cleaned_data


class CautelaArmaForm(forms.ModelForm):
    """Formulário para registro de cautela de arma"""
    
    class Meta:
        model = CautelaArma
        fields = [
            'arma', 'militar', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'quantidade_carregadores', 'numeracao_carregadores', 'quantidade_municoes_catalogadas',
            'observacoes'
        ]
        widgets = {
            'arma': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_arma_cautela'
            }),
            'militar': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_militar_cautela'
            }),
            'orgao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_orgao_cautela'
            }),
            'grande_comando': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_grande_comando_cautela'
            }),
            'unidade': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_unidade_cautela'
            }),
            'sub_unidade': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_sub_unidade_cautela'
            }),
            'quantidade_carregadores': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Quantidade de carregadores'
            }),
            'numeracao_carregadores': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Digite a numeração de cada carregador, separada por vírgula ou quebra de linha'
            }),
            'quantidade_municoes_catalogadas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Quantidade de munições'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações sobre a cautela...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas armas que podem ser cauteladas (ativas, não em cautela e não inservíveis)
        self.fields['arma'].queryset = Arma.objects.filter(
            ativo=True
        ).exclude(
            situacao='CAUTELA_INDIVIDUAL'
        ).exclude(
            estado_conservacao='INSERVIVEL'
        ).order_by('numero_serie')
        self.fields['arma'].empty_label = 'Selecione uma arma'
        self.fields['arma'].required = True
        
        # Permitir qualquer militar ativo (o Select2 vai fazer a busca e validação)
        # Não limitar o queryset aqui para permitir que o Select2 funcione corretamente
        # A validação será feita no método clean_militar
        self.fields['militar'].queryset = Militar.objects.all().order_by('nome_completo')
        self.fields['militar'].empty_label = 'Selecione um militar'
        
        # Tornar campos de organização opcionais
        self.fields['orgao'].required = False
        self.fields['grande_comando'].required = False
        self.fields['unidade'].required = False
        self.fields['sub_unidade'].required = False
    
    def clean_militar(self):
        """Valida o militar selecionado"""
        militar = self.cleaned_data.get('militar')
        
        if militar:
            # Verificar se o militar existe e está ativo (usar classificacao, não situacao)
            if militar.classificacao != 'ATIVO':
                raise forms.ValidationError('Apenas militares ativos podem receber armas em cautela.')
        
        return militar
    
    def clean_arma(self):
        """Valida a arma selecionada"""
        arma = self.cleaned_data.get('arma')
        
        if arma:
            # Verificar se a arma está ativa
            if not arma.ativo:
                raise forms.ValidationError('Apenas armas ativas podem ser cauteladas.')
            
            # Verificar se a arma não está em cautela individual
            if arma.situacao == 'CAUTELA_INDIVIDUAL':
                raise forms.ValidationError('Esta arma já está em cautela individual.')
            
            # Verificar se a arma não está inservível
            if arma.estado_conservacao == 'INSERVIVEL':
                raise forms.ValidationError('Armas inservíveis não podem ser cauteladas.')
        
        return arma
    
    def clean(self):
        cleaned_data = super().clean()
        arma = cleaned_data.get('arma')
        militar = cleaned_data.get('militar')
        
        # Validar que uma arma foi selecionada
        if not arma:
            raise forms.ValidationError('É obrigatório selecionar uma arma para a cautela.')
        
        if arma and militar:
            # Verificar se a arma já está em cautela
            if arma.situacao == 'CAUTELA_INDIVIDUAL':
                raise forms.ValidationError('Esta arma já está em cautela com outro militar.')
            
            # Verificar se o militar já tem cautela ativa com esta arma
            cautela_ativa = CautelaArma.objects.filter(
                arma=arma,
                militar=militar,
                ativa=True
            ).exists()
            
            if cautela_ativa:
                raise forms.ValidationError('Este militar já possui uma cautela ativa para esta arma.')
        
        return cleaned_data


class CautelaArmaColetivaForm(forms.ModelForm):
    """Formulário para registro de cautela coletiva de armas"""
    
    class Meta:
        from .models import CautelaArmaColetiva
        model = CautelaArmaColetiva
        fields = [
            'descricao', 'tipo_finalidade', 'responsavel',
            'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'data_inicio', 'documento_referencia', 'observacoes'
        ]
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Instrução de tiro, Operação X, etc'
            }),
            'tipo_finalidade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsavel': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_responsavel_coletiva'
            }),
            'orgao': forms.HiddenInput(),
            'grande_comando': forms.HiddenInput(),
            'unidade': forms.HiddenInput(),
            'sub_unidade': forms.HiddenInput(),
            'data_inicio': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'documento_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Portaria nº 123/2024, Ofício nº 456/2024, etc'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações sobre a cautela coletiva...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas militares ativos
        self.fields['responsavel'].queryset = Militar.objects.filter(
            classificacao='ATIVO'
        ).order_by('nome_completo')
        self.fields['responsavel'].empty_label = 'Selecione um militar'
        
        # Tornar campos de organização opcionais e ocultos (serão preenchidos via JavaScript)
        self.fields['orgao'].required = False
        self.fields['grande_comando'].required = False
        self.fields['unidade'].required = False
        self.fields['sub_unidade'].required = False


class CautelaArmaColetivaItemForm(forms.ModelForm):
    """Formulário para adicionar uma arma a uma cautela coletiva"""
    
    class Meta:
        from .models import CautelaArmaColetivaItem
        model = CautelaArmaColetivaItem
        fields = [
            'arma', 'quantidade_carregadores', 'numeracao_carregadores',
            'quantidade_municoes_catalogadas', 'observacoes'
        ]
        widgets = {
            'arma': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_arma_coletiva'
            }),
            'quantidade_carregadores': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Quantidade de carregadores'
            }),
            'numeracao_carregadores': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Digite a numeração de cada carregador, separada por vírgula ou quebra de linha'
            }),
            'quantidade_municoes_catalogadas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Quantidade de munições'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre esta arma...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        cautela = kwargs.pop('cautela', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas armas que podem ser cauteladas
        queryset = Arma.objects.filter(
            ativo=True,
            situacao='RESERVA_ARMAMENTO'
        ).order_by('numero_serie')
        
        # Se já existe uma cautela, excluir armas que já estão nela
        if cautela and cautela.pk:
            armas_na_cautela = cautela.armas.values_list('arma_id', flat=True)
            queryset = queryset.exclude(id__in=armas_na_cautela)
        
        self.fields['arma'].queryset = queryset
        self.fields['arma'].empty_label = 'Selecione uma arma'
    
    def clean_arma(self):
        """Valida se a arma pode ser adicionada"""
        arma = self.cleaned_data.get('arma')
        
        if arma:
            if not arma.ativo:
                raise forms.ValidationError('Apenas armas ativas podem ser cauteladas.')
        
        return arma


class DevolucaoCautelaArmaForm(forms.ModelForm):
    """Formulário para devolução de cautela de arma"""
    
    class Meta:
        model = CautelaArma
        fields = ['observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações sobre a devolução...'
            }),
        }


class ConfiguracaoArmaForm(forms.ModelForm):
    """Formulário para cadastro e edição de configurações de armas"""
    
    class Meta:
        model = ConfiguracaoArma
        fields = ['imagem', 'tipo', 'tipo_acessorio', 'calibre', 'marca', 'modelo', 'ativo']
        widgets = {
            'imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo'
            }),
            'tipo_acessorio': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_acessorio'
            }),
            'calibre': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Taurus, Glock, IMBEL'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PT 100 AF, PT 100 PLUS, 24/7 PRO'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar tipo_acessorio obrigatório apenas quando tipo for ACESSORIO
        self.fields['tipo_acessorio'].required = False
        self.fields['calibre'].required = False
        
        
        # Se for edição e já for acessório, tornar obrigatório
        if self.instance and self.instance.pk and self.instance.tipo == 'ACESSORIO':
            self.fields['tipo_acessorio'].required = True
        elif self.instance and self.instance.pk:
            # Se não for acessório, limpar o campo
            self.initial['tipo_acessorio'] = None
    
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        tipo_acessorio = cleaned_data.get('tipo_acessorio')
        calibre = cleaned_data.get('calibre')
        
        # Se for acessório, tipo_acessorio é obrigatório
        if tipo == 'ACESSORIO':
            if not tipo_acessorio:
                raise forms.ValidationError('Para acessórios, é necessário selecionar o tipo de acessório.')
            # Calibre não é obrigatório para acessórios
            if not calibre:
                cleaned_data['calibre'] = None
        else:
            # Se não for acessório, limpar tipo_acessorio
            if tipo_acessorio:
                cleaned_data['tipo_acessorio'] = None
            # Calibre é obrigatório para armas
            if not calibre:
                raise forms.ValidationError('Para armas, é necessário selecionar o calibre.')
        
        return cleaned_data


class ConfiguracaoMunicaoForm(forms.ModelForm):
    """Formulário para cadastro e edição de configurações de munições"""
    
    class Meta:
        model = ConfiguracaoMunicao
        fields = ['imagem', 'calibre', 'tipo_municao', 'marca', 'modelo', 'descricao', 'ativo']
        widgets = {
            'imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'calibre': forms.Select(attrs={
                'class': 'form-select',
                'data-allow-custom': 'true'
            }),
            'tipo_municao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: CBC, Magtech, Federal'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: FMJ 115gr, HP 124gr'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição adicional da munição (opcional)'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_calibre(self):
        """Permitir valores customizados para calibre"""
        calibre = self.cleaned_data.get('calibre')
        if calibre:
            return calibre
        return calibre


class MunicaoForm(forms.ModelForm):
    """Formulário para cadastro de munição"""
    
    class Meta:
        model = Municao
        fields = ['calibre', 'orgao', 'grande_comando', 'unidade', 'sub_unidade', 'quantidade_estoque']
        widgets = {
            'calibre': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_calibre_municao'
            }),
            'orgao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_orgao_municao'
            }),
            'grande_comando': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_grande_comando_municao'
            }),
            'unidade': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_unidade_municao'
            }),
            'sub_unidade': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_sub_unidade_municao'
            }),
            'quantidade_estoque': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Quantidade inicial em estoque'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair request do kwargs se presente
        self.request = kwargs.pop('request', None)
        
        super().__init__(*args, **kwargs)
        self.fields['orgao'].required = False
        self.fields['grande_comando'].required = False
        self.fields['unidade'].required = False
        self.fields['sub_unidade'].required = False
        self.fields['quantidade_estoque'].required = False
        self.fields['quantidade_estoque'].initial = 0
        
        # Configurar campos de OM como ocultos apenas se for requisição AJAX (modal)
        try:
            if self.request and hasattr(self.request, 'headers') and self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                self.fields['orgao'].widget = forms.HiddenInput()
                self.fields['grande_comando'].widget = forms.HiddenInput()
                self.fields['unidade'].widget = forms.HiddenInput()
                self.fields['sub_unidade'].widget = forms.HiddenInput()
        except Exception:
            # Se houver erro ao verificar headers, manter campos visíveis (formulário tradicional)
            pass


class EntradaMunicaoForm(forms.ModelForm):
    """Formulário para registro de entrada de munição"""
    
    class Meta:
        model = EntradaMunicao
        fields = ['municao', 'quantidade', 'data_entrada', 'observacoes']
        widgets = {
            'municao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_municao_entrada'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Quantidade de munições'
            }),
            'data_entrada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a entrada...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar munições por calibre
        self.fields['municao'].queryset = Municao.objects.all().order_by('calibre')
        self.fields['municao'].empty_label = 'Selecione uma munição'
        
        # Configurar data inicial (timezone de Brasília)
        try:
            import pytz
            brasilia_tz = pytz.timezone('America/Sao_Paulo')
            now = timezone.now()
            if timezone.is_aware(now):
                agora_brasilia = now.astimezone(brasilia_tz)
            else:
                agora_brasilia = brasilia_tz.localize(now)
            self.fields['data_entrada'].initial = agora_brasilia.strftime('%Y-%m-%dT%H:%M')
        except Exception:
            # Se houver erro, deixar vazio
            pass
        
        self.fields['observacoes'].required = False


class SaidaMunicaoForm(forms.ModelForm):
    """Formulário para registro de saída de munição"""
    
    class Meta:
        model = SaidaMunicao
        fields = ['municao', 'quantidade', 'tipo_saida', 'cautela_individual', 'cautela_coletiva', 'data_saida', 'observacoes']
        widgets = {
            'municao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_municao_saida'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Quantidade de munições'
            }),
            'tipo_saida': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_saida'
            }),
            'cautela_individual': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_cautela_individual_saida'
            }),
            'cautela_coletiva': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_cautela_coletiva_saida'
            }),
            'data_saida': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a saída...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_saida'].initial = timezone.now()
        self.fields['cautela_individual'].required = False
        self.fields['cautela_individual'].queryset = CautelaArma.objects.filter(ativa=True).order_by('-data_entrega')
        self.fields['cautela_individual'].empty_label = 'Nenhuma (selecionar se for cautela individual)'
        self.fields['cautela_coletiva'].required = False
        self.fields['cautela_coletiva'].queryset = CautelaArmaColetiva.objects.filter(ativa=True).order_by('-data_inicio')
        self.fields['cautela_coletiva'].empty_label = 'Nenhuma (selecionar se for cautela coletiva)'
        self.fields['observacoes'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_saida = cleaned_data.get('tipo_saida')
        cautela_individual = cleaned_data.get('cautela_individual')
        cautela_coletiva = cleaned_data.get('cautela_coletiva')
        
        # Validar relacionamento com cautela
        if tipo_saida == 'CAUTELA_INDIVIDUAL' and not cautela_individual:
            raise forms.ValidationError('Para saída de tipo Cautela Individual, é necessário selecionar uma cautela individual.')
        if tipo_saida == 'CAUTELA_COLETIVA' and not cautela_coletiva:
            raise forms.ValidationError('Para saída de tipo Cautela Coletiva, é necessário selecionar uma cautela coletiva.')
        
        # Limpar cautela que não corresponde ao tipo
        if tipo_saida != 'CAUTELA_INDIVIDUAL':
            cleaned_data['cautela_individual'] = None
        if tipo_saida != 'CAUTELA_COLETIVA':
            cleaned_data['cautela_coletiva'] = None
        
        return cleaned_data


class DevolucaoMunicaoForm(forms.ModelForm):
    """Formulário para registro de devolução de munição"""
    
    class Meta:
        model = DevolucaoMunicao
        fields = ['saida', 'quantidade_devolvida', 'data_devolucao', 'observacoes']
        widgets = {
            'saida': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_saida_devolucao'
            }),
            'quantidade_devolvida': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Quantidade de munições a devolver'
            }),
            'data_devolucao': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a devolução...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_devolucao'].initial = timezone.now()
        # Filtrar apenas saídas que ainda têm quantidade pendente
        from django.db import models as db_models
        self.fields['saida'].queryset = SaidaMunicao.objects.filter(
            totalmente_devolvida=False
        ).annotate(
            pendente=db_models.F('quantidade') - db_models.F('quantidade_devolvida')
        ).filter(
            pendente__gt=0
        ).order_by('-data_saida')
        self.fields['saida'].empty_label = 'Selecione uma saída'
        self.fields['observacoes'].required = False
    
    def clean_quantidade_devolvida(self):
        quantidade_devolvida = self.cleaned_data.get('quantidade_devolvida')
        saida = self.cleaned_data.get('saida')
        
        if saida and quantidade_devolvida:
            quantidade_pendente = saida.get_quantidade_pendente()
            if quantidade_devolvida > quantidade_pendente:
                raise forms.ValidationError(
                    f'Quantidade de devolução excede o pendente. Pendente: {quantidade_pendente}, Tentando devolver: {quantidade_devolvida}'
                )
        
        return quantidade_devolvida


class CautelaMunicaoForm(forms.ModelForm):
    """Formulário para registro de cautela de munição"""
    
    class Meta:
        model = CautelaMunicao
        fields = [
            'municao', 'militar', 'quantidade', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'observacoes'
        ]
        widgets = {
            'municao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_municao_cautela'
            }),
            'militar': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_militar_cautela_municao'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Quantidade de munições'
            }),
            'orgao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_orgao_cautela_municao'
            }),
            'grande_comando': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_grande_comando_cautela_municao'
            }),
            'unidade': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_unidade_cautela_municao'
            }),
            'sub_unidade': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_sub_unidade_cautela_municao'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações sobre a cautela...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas munições com estoque disponível
        self.fields['municao'].queryset = Municao.objects.filter(quantidade_estoque__gt=0).order_by('calibre')
        self.fields['municao'].empty_label = 'Selecione uma munição'
        self.fields['municao'].required = True
        
        # Permitir qualquer militar ativo
        self.fields['militar'].queryset = Militar.objects.filter(classificacao='ATIVO').order_by('nome_completo')
        self.fields['militar'].empty_label = 'Selecione um militar'
        
        # Tornar campos de organização opcionais
        self.fields['orgao'].required = False
        self.fields['grande_comando'].required = False
        self.fields['unidade'].required = False
        self.fields['sub_unidade'].required = False
    
    def clean_militar(self):
        """Valida o militar selecionado"""
        militar = self.cleaned_data.get('militar')
        
        if militar:
            if militar.classificacao != 'ATIVO':
                raise forms.ValidationError('Apenas militares ativos podem receber munições em cautela.')
        
        return militar
    
    def clean_quantidade(self):
        """Valida a quantidade"""
        quantidade = self.cleaned_data.get('quantidade')
        municao = self.cleaned_data.get('municao')
        
        if quantidade and municao:
            if quantidade > municao.quantidade_estoque:
                raise forms.ValidationError(
                    f'Quantidade solicitada ({quantidade}) excede o estoque disponível ({municao.quantidade_estoque}).'
                )
        
        return quantidade
    
    def clean(self):
        cleaned_data = super().clean()
        municao = cleaned_data.get('municao')
        militar = cleaned_data.get('militar')
        quantidade = cleaned_data.get('quantidade')
        
        if not municao:
            raise forms.ValidationError('É obrigatório selecionar uma munição para a cautela.')
        
        if not militar:
            raise forms.ValidationError('É obrigatório selecionar um militar para a cautela.')
        
        if not quantidade or quantidade <= 0:
            raise forms.ValidationError('A quantidade deve ser maior que zero.')
        
        return cleaned_data


class DevolucaoCautelaMunicaoForm(forms.ModelForm):
    """Formulário para devolução de cautela de munição"""
    
    quantidade_devolvida = forms.IntegerField(
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'id': 'id_quantidade_devolvida_devolucao'
        })
    )
    
    class Meta:
        model = CautelaMunicao
        fields = ['quantidade_devolvida', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações sobre a devolução...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.cautela = kwargs.pop('cautela', None)
        super().__init__(*args, **kwargs)
        if self.cautela:
            quantidade_pendente = self.cautela.get_quantidade_pendente()
            self.fields['quantidade_devolvida'].help_text = f'Quantidade pendente: {quantidade_pendente}'
            self.fields['quantidade_devolvida'].widget.attrs['max'] = quantidade_pendente
    
    def clean_quantidade_devolvida(self):
        quantidade_devolvida = self.cleaned_data.get('quantidade_devolvida')
        
        if self.cautela:
            quantidade_pendente = self.cautela.get_quantidade_pendente()
            if quantidade_devolvida > quantidade_pendente:
                raise forms.ValidationError(
                    f'Quantidade de devolução ({quantidade_devolvida}) excede o pendente ({quantidade_pendente}).'
                )
        
        return quantidade_devolvida


# ============================================================================
# FORMULÁRIOS PARA TOMBAMENTO DE BENS MÓVEIS
# ============================================================================

class BemMovelForm(forms.ModelForm):
    """Formulário para cadastro e edição de bens móveis"""
    
    # Campo para seleção hierárquica do organograma (não é salvo diretamente)
    organograma_select = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'organograma-select'
        })
    )
    
    class Meta:
        from .models import BemMovel
        model = BemMovel
        fields = [
            'numero_tombamento', 'descricao', 'categoria', 'marca', 'modelo',
            'numero_serie', 'patrimonio', 'orgao', 'grande_comando', 'unidade', 
            'sub_unidade', 'localizacao_detalhada', 'data_aquisicao', 
            'valor_aquisicao', 'fornecedor', 'nota_fiscal', 'situacao',
            'responsavel_atual', 'observacoes', 'ativo'
        ]
        widgets = {
            'numero_tombamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 001/2024',
                'style': 'text-transform: uppercase;'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição detalhada do bem móvel'
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Dell, HP, Samsung'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: OptiPlex 7090'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de série do equipamento'
            }),
            'patrimonio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de patrimônio'
            }),
            'orgao': forms.Select(attrs={'class': 'form-select'}),
            'grande_comando': forms.Select(attrs={'class': 'form-select'}),
            'unidade': forms.Select(attrs={'class': 'form-select'}),
            'sub_unidade': forms.Select(attrs={'class': 'form-select'}),
            'localizacao_detalhada': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Sala 101, Almoxarifado'
            }),
            'data_aquisicao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_data_aquisicao'
            }),
            'valor_aquisicao': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_aquisicao',
                'placeholder': '0,00',
                'type': 'text'
            }),
            'fornecedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do fornecedor'
            }),
            'nota_fiscal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da nota fiscal'
            }),
            'situacao': forms.Select(attrs={'class': 'form-select'}),
            'responsavel_atual': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre o bem móvel...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Tornar campos opcionais
        self.fields['orgao'].required = False
        self.fields['grande_comando'].required = False
        self.fields['unidade'].required = False
        self.fields['sub_unidade'].required = False
        self.fields['responsavel_atual'].required = False
        
        # Configurar data de aquisição
        if 'data_aquisicao' in self.fields:
            self.fields['data_aquisicao'].widget.format = '%Y-%m-%d'
            if self.instance and self.instance.pk and self.instance.data_aquisicao:
                try:
                    self.initial['data_aquisicao'] = self.instance.data_aquisicao.strftime('%Y-%m-%d')
                except:
                    pass


class TombamentoBemMovelForm(forms.ModelForm):
    """Formulário para registro de tombamento de bens móveis"""
    
    class Meta:
        from .models import TombamentoBemMovel
        model = TombamentoBemMovel
        fields = [
            'bem_movel', 'tipo_tombamento', 'data_tombamento',
            'orgao_origem', 'grande_comando_origem', 'unidade_origem', 'sub_unidade_origem',
            'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino',
            'responsavel_origem', 'responsavel_destino', 'valor_atual', 'observacoes', 'ativo'
        ]
        widgets = {
            'bem_movel': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'tipo_tombamento': forms.Select(attrs={'class': 'form-select'}),
            'data_tombamento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_data_tombamento'
            }),
            'orgao_origem': forms.Select(attrs={'class': 'form-select'}),
            'grande_comando_origem': forms.Select(attrs={'class': 'form-select'}),
            'unidade_origem': forms.Select(attrs={'class': 'form-select'}),
            'sub_unidade_origem': forms.Select(attrs={'class': 'form-select'}),
            'orgao_destino': forms.Select(attrs={'class': 'form-select'}),
            'grande_comando_destino': forms.Select(attrs={'class': 'form-select'}),
            'unidade_destino': forms.Select(attrs={'class': 'form-select'}),
            'sub_unidade_destino': forms.Select(attrs={'class': 'form-select'}),
            'responsavel_origem': forms.Select(attrs={'class': 'form-select'}),
            'responsavel_destino': forms.Select(attrs={'class': 'form-select'}),
            'valor_atual': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_atual',
                'placeholder': '0,00',
                'type': 'text'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre o tombamento...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Tornar campos opcionais
        self.fields['orgao_origem'].required = False
        self.fields['grande_comando_origem'].required = False
        self.fields['unidade_origem'].required = False
        self.fields['sub_unidade_origem'].required = False
        self.fields['orgao_destino'].required = False
        self.fields['grande_comando_destino'].required = False
        self.fields['unidade_destino'].required = False
        self.fields['sub_unidade_destino'].required = False
        self.fields['responsavel_origem'].required = False
        self.fields['responsavel_destino'].required = False
        
        # Configurar data de tombamento
        if 'data_tombamento' in self.fields:
            self.fields['data_tombamento'].widget.format = '%Y-%m-%d'
            if not self.instance.pk:
                from datetime import date
                self.initial['data_tombamento'] = date.today().strftime('%Y-%m-%d')
            elif self.instance and self.instance.pk and self.instance.data_tombamento:
                try:
                    self.initial['data_tombamento'] = self.instance.data_tombamento.strftime('%Y-%m-%d')
                except:
                    pass


# ============================================================================
# FORMULÁRIOS PARA ALMOXARIFADO
# ============================================================================

class ProdutoAlmoxarifadoForm(forms.ModelForm):
    """Formulário para cadastro e edição de itens do almoxarifado"""
    
    # Sobrescrever valor_unitario para aceitar string (formato brasileiro)
    valor_unitario = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_valor_unitario',
            'placeholder': '0,00',
            'type': 'text'
        })
    )
    
    # Campo código como oculto para preservar na edição
    codigo = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    class Meta:
        from .models import ProdutoAlmoxarifado
        model = ProdutoAlmoxarifado
        fields = [
            'codigo', 'codigo_barras', 'descricao', 'categoria', 'subcategoria', 'unidade_medida', 'marca', 'modelo', 'tamanho',
            'estoque_minimo', 'estoque_maximo', 'quantidade_inicial', 'quantidade_atual', 'localizacao',
            'valor_unitario', 'fornecedor_principal', 'imagem', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'observacoes', 'ativo'
        ]
        widgets = {
            'codigo_barras': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ler com leitor ou digitar',
                'id': 'id_codigo_barras'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição detalhada do item'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_categoria'
            }),
            'subcategoria': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_subcategoria'
            }),
            'unidade_medida': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca do item'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo do item'
            }),
            'tamanho': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 35, 36, 37, P, M, G, GG, etc. (cada tamanho diferente é um item individual)'
            }),
            'estoque_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'estoque_maximo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'quantidade_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'help_text': 'Quantidade inicial em estoque (estoque inicial definido quando o item foi criado)'
            }),
            'quantidade_atual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'readonly': True,
                'help_text': 'Quantidade atual calculada automaticamente (inicial + entradas - saídas)'
            }),
            'localizacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Prateleira A, Gaveta 3'
            }),
            'fornecedor_principal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do fornecedor principal'
            }),
            'imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_imagem'
            }),
            'orgao': forms.Select(attrs={'class': 'form-select'}),
            'grande_comando': forms.Select(attrs={'class': 'form-select'}),
            'unidade': forms.Select(attrs={'class': 'form-select'}),
            'sub_unidade': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre o item...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar subcategorias baseado na categoria selecionada
        from .models import Categoria, Subcategoria
        
        self.fields['categoria'].queryset = Categoria.objects.filter(ativo=True).order_by('nome')
        self.fields['categoria'].required = False
        
        # Inicializar queryset vazio, será atualizado no clean() ou quando categoria for selecionada
        self.fields['subcategoria'].queryset = Subcategoria.objects.none()
        self.fields['subcategoria'].required = False
        
        # Se já tiver dados no POST, tentar atualizar o queryset baseado na categoria
        if self.data and 'categoria' in self.data:
            categoria_id = self.data.get('categoria')
            if categoria_id:
                try:
                    categoria_obj = Categoria.objects.get(pk=categoria_id, ativo=True)
                    self.fields['subcategoria'].queryset = Subcategoria.objects.filter(
                        categoria=categoria_obj,
                        ativo=True
                    ).order_by('nome')
                except (Categoria.DoesNotExist, ValueError):
                    pass
        
        # Configurar campo código de barras (opcional)
        self.fields['codigo_barras'].required = False
        self.fields['codigo_barras'].help_text = 'Leia com o leitor de código de barras ou digite manualmente'
        
        # Configurar quantidade_inicial e quantidade_atual
        # quantidade_inicial é obrigatório para novos itens
        if not self.instance or not self.instance.pk:
            self.fields['quantidade_inicial'].required = True
        else:
            self.fields['quantidade_inicial'].required = False
        
        # quantidade_atual é somente leitura (calculado automaticamente)
        self.fields['quantidade_atual'].widget.attrs['readonly'] = True
        self.fields['quantidade_atual'].required = False
        
        # Configurar querysets dos campos de OM para todos os usuários verem todas as OMs ativas
        from .models import Orgao, GrandeComando, Unidade, SubUnidade
        
        self.fields['orgao'].queryset = Orgao.objects.filter(ativo=True).order_by('nome')
        self.fields['orgao'].empty_label = 'Selecione um órgão'
        self.fields['orgao'].required = False
        
        self.fields['grande_comando'].queryset = GrandeComando.objects.filter(ativo=True).order_by('orgao__nome', 'nome')
        self.fields['grande_comando'].empty_label = 'Selecione um grande comando'
        self.fields['grande_comando'].required = False
        
        self.fields['unidade'].queryset = Unidade.objects.filter(ativo=True).order_by('grande_comando__orgao__nome', 'grande_comando__nome', 'nome')
        self.fields['unidade'].empty_label = 'Selecione uma unidade'
        self.fields['unidade'].required = False
        
        self.fields['sub_unidade'].queryset = SubUnidade.objects.filter(ativo=True).order_by('unidade__grande_comando__orgao__nome', 'unidade__grande_comando__nome', 'unidade__nome', 'nome')
        self.fields['sub_unidade'].empty_label = 'Selecione uma sub-unidade'
        self.fields['sub_unidade'].required = False
        
        # Se for criação e não tiver OM preenchida, preencher com a OM da função do usuário
        if not self.instance.pk and self.request:
            from .permissoes_militares import obter_sessao_ativa_usuario
            sessao = obter_sessao_ativa_usuario(self.request.user)
            if sessao and sessao.funcao_militar_usuario:
                funcao = sessao.funcao_militar_usuario
                # Usar self.initial se não houver dados no POST
                if not self.data:
                    if not self.initial.get('orgao') and funcao.orgao:
                        self.initial['orgao'] = funcao.orgao.pk
                    if not self.initial.get('grande_comando') and funcao.grande_comando:
                        self.initial['grande_comando'] = funcao.grande_comando.pk
                    if not self.initial.get('unidade') and funcao.unidade:
                        self.initial['unidade'] = funcao.unidade.pk
                    if not self.initial.get('sub_unidade') and funcao.sub_unidade:
                        self.initial['sub_unidade'] = funcao.sub_unidade.pk
                
                # Também definir os valores nos campos diretamente para garantir que sejam exibidos
                if funcao.orgao and not self.data:
                    self.fields['orgao'].initial = funcao.orgao.pk
                if funcao.grande_comando and not self.data:
                    self.fields['grande_comando'].initial = funcao.grande_comando.pk
                if funcao.unidade and not self.data:
                    self.fields['unidade'].initial = funcao.unidade.pk
                if funcao.sub_unidade and not self.data:
                    self.fields['sub_unidade'].initial = funcao.sub_unidade.pk
        
        # Se estiver editando e já tiver categoria/subcategoria, carregar as opções
        if self.instance and self.instance.pk:
            if self.instance.categoria:
                queryset = Subcategoria.objects.filter(
                    categoria=self.instance.categoria,
                    ativo=True
                ).order_by('nome')
                
                # Se já tiver subcategoria selecionada, garantir que está no queryset
                if self.instance.subcategoria:
                    subcategoria_id = self.instance.subcategoria.pk
                    if subcategoria_id not in queryset.values_list('pk', flat=True):
                        # Adicionar a subcategoria atual ao queryset mesmo que não esteja ativa
                        from django.db.models import Q
                        queryset = Subcategoria.objects.filter(
                            Q(categoria=self.instance.categoria, ativo=True) |
                            Q(pk=subcategoria_id)
                        ).order_by('nome')
                
                self.fields['subcategoria'].queryset = queryset
                
                # Garantir que o valor inicial da subcategoria está definido
                if self.instance.subcategoria:
                    self.initial['subcategoria'] = self.instance.subcategoria.pk
            
            # Formatar valor unitário para exibição (ponto para vírgula)
            if self.instance.valor_unitario:
                self.initial['valor_unitario'] = str(self.instance.valor_unitario).replace('.', ',')
    
    def clean(self):
        """Validação customizada do formulário"""
        cleaned_data = super().clean()
        
        # Se quantidade_inicial não foi preenchida mas quantidade_atual foi,
        # usar quantidade_atual como quantidade_inicial
        quantidade_inicial = cleaned_data.get('quantidade_inicial')
        quantidade_atual = cleaned_data.get('quantidade_atual')
        
        if (not quantidade_inicial or quantidade_inicial == 0) and quantidade_atual and quantidade_atual > 0:
            cleaned_data['quantidade_inicial'] = quantidade_atual
        
        # Se quantidade_inicial foi preenchida mas quantidade_atual não,
        # usar quantidade_inicial como quantidade_atual (para novos itens)
        if quantidade_inicial and quantidade_inicial > 0 and (not quantidade_atual or quantidade_atual == 0):
            cleaned_data['quantidade_atual'] = quantidade_inicial
        
        categoria = cleaned_data.get('categoria')
        subcategoria_value = cleaned_data.get('subcategoria')
        
        # Importar aqui para evitar problemas de importação circular
        from .models import Subcategoria
        from django.db.models import Q
        
        # Se uma subcategoria foi selecionada, atualizar o queryset baseado na categoria
        if categoria and subcategoria_value:
            try:
                # Obter o ID da subcategoria (pode ser um objeto ou um ID)
                if isinstance(subcategoria_value, Subcategoria):
                    subcategoria = subcategoria_value
                    subcategoria_id = subcategoria.pk
                else:
                    subcategoria_id = subcategoria_value
                    subcategoria = Subcategoria.objects.get(pk=subcategoria_id)
                
                # Verificar se a subcategoria pertence à categoria
                if subcategoria.categoria != categoria:
                    raise forms.ValidationError({
                        'subcategoria': 'A subcategoria selecionada não pertence à categoria escolhida.'
                    })
                
                # Atualizar o queryset para incluir a subcategoria selecionada
                queryset = Subcategoria.objects.filter(
                    Q(categoria=categoria, ativo=True) |
                    Q(pk=subcategoria_id, categoria=categoria)
                ).order_by('nome')
                
                # Atualizar o queryset do campo para permitir a validação
                self.fields['subcategoria'].queryset = queryset
            except (Subcategoria.DoesNotExist, ValueError, TypeError) as e:
                # Se não conseguir encontrar a subcategoria, limpar o campo
                cleaned_data['subcategoria'] = None
        elif categoria:
            # Se só tem categoria, atualizar o queryset
            self.fields['subcategoria'].queryset = Subcategoria.objects.filter(
                categoria=categoria,
                ativo=True
            ).order_by('nome')
        
        return cleaned_data
    
    def clean_valor_unitario(self):
        """Converte vírgula para ponto no valor unitário (formato brasileiro)"""
        valor = self.cleaned_data.get('valor_unitario')
        if valor:
            # Se for string, converter formato brasileiro (1.234,56) para formato Django (1234.56)
            if isinstance(valor, str):
                # Remover espaços
                valor = valor.strip()
                if not valor:
                    return None
                
                # Se tiver vírgula, é formato brasileiro
                if ',' in valor:
                    # Remover pontos (separadores de milhares) e substituir vírgula por ponto
                    valor = valor.replace('.', '').replace(',', '.')
                # Se não tiver vírgula mas tiver ponto, verificar se é decimal ou separador de milhares
                elif '.' in valor:
                    # Se tiver mais de um ponto, são separadores de milhares (formato americano)
                    if valor.count('.') > 1:
                        # Remover todos os pontos exceto o último
                        partes = valor.split('.')
                        valor = ''.join(partes[:-1]) + '.' + partes[-1]
                    # Se tiver apenas um ponto, já está no formato correto
                
            try:
                from decimal import Decimal
                decimal_valor = Decimal(str(valor))
                # Validar que não é negativo
                if decimal_valor < 0:
                    raise forms.ValidationError('O valor não pode ser negativo.')
                return decimal_valor
            except (ValueError, TypeError) as e:
                raise forms.ValidationError('Informe um valor numérico válido. Exemplo: 5,00 ou 1.234,56')
        return None


class EntradaAlmoxarifadoForm(forms.ModelForm):
    """Formulário para registro de entrada de materiais no almoxarifado"""
    
    class Meta:
        from .models import EntradaAlmoxarifado
        model = EntradaAlmoxarifado
        fields = [
            'produto', 'tipo_entrada', 'data_entrada', 'quantidade',
            'fornecedor', 'cnpj_fornecedor', 'endereco_fornecedor', 'nota_fiscal',
            'numero_processo', 'numero_convenio',
            'orgao_origem', 'grande_comando_origem',
            'unidade_origem', 'sub_unidade_origem', 'orgao_destino', 'grande_comando_destino',
            'unidade_destino', 'sub_unidade_destino', 'responsavel', 'observacoes', 'ativo'
        ]
        widgets = {
            'produto': forms.Select(attrs={
                'class': 'form-select',
                # Não obrigatório - múltiplos produtos via produtos_entrada
            }),
            'tipo_entrada': forms.Select(attrs={'class': 'form-select'}),
            'data_entrada': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_data_entrada'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                # Não obrigatório - quantidade calculada dos produtos
            }),
            'fornecedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do fornecedor'
            }),
            'cnpj_fornecedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XX.XXX.XXX/XXXX-XX'
            }),
            'endereco_fornecedor': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Endereço completo do fornecedor (rua, número, bairro, cidade, estado, CEP)'
            }),
            'nota_fiscal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da nota fiscal'
            }),
            'numero_processo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do processo (obrigatório para doações)'
            }),
            'numero_convenio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do convênio (obrigatório para doações)'
            }),
            'orgao_origem': forms.Select(attrs={'class': 'form-select'}),
            'grande_comando_origem': forms.Select(attrs={'class': 'form-select'}),
            'unidade_origem': forms.Select(attrs={'class': 'form-select'}),
            'sub_unidade_origem': forms.Select(attrs={'class': 'form-select'}),
            'orgao_destino': forms.Select(attrs={'class': 'form-select'}),
            'grande_comando_destino': forms.Select(attrs={'class': 'form-select'}),
            'unidade_destino': forms.Select(attrs={'class': 'form-select'}),
            'sub_unidade_destino': forms.Select(attrs={'class': 'form-select'}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a entrada...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Tornar campos opcionais
        self.fields['produto'].required = False  # Múltiplos produtos são gerenciados via JavaScript
        self.fields['quantidade'].required = False  # Quantidade é calculada pelos itens
        self.fields['orgao_origem'].required = False
        self.fields['grande_comando_origem'].required = False
        self.fields['unidade_origem'].required = False
        self.fields['sub_unidade_origem'].required = False
        self.fields['orgao_destino'].required = False
        self.fields['grande_comando_destino'].required = False
        self.fields['unidade_destino'].required = False
        self.fields['sub_unidade_destino'].required = False
        self.fields['responsavel'].required = False
        self.fields['cnpj_fornecedor'].required = False
        self.fields['endereco_fornecedor'].required = False
        self.fields['numero_processo'].required = False
        self.fields['numero_convenio'].required = False
        
        # Configurar data de entrada
        if 'data_entrada' in self.fields:
            self.fields['data_entrada'].widget.format = '%Y-%m-%d'
            if not self.instance.pk:
                from datetime import date
                self.initial['data_entrada'] = date.today().strftime('%Y-%m-%d')
            elif self.instance and self.instance.pk and self.instance.data_entrada:
                try:
                    self.initial['data_entrada'] = self.instance.data_entrada.strftime('%Y-%m-%d')
                except:
                    pass
        
        # Preencher OM de destino com a OM da função do usuário (apenas na criação)
        if not self.instance.pk and self.request and self.request.user:
            from .permissoes_militares import obter_sessao_ativa_usuario
            sessao = obter_sessao_ativa_usuario(self.request.user)
            if sessao and sessao.funcao_militar_usuario:
                funcao = sessao.funcao_militar_usuario
                # Preencher com a OM mais específica disponível
                if funcao.sub_unidade:
                    self.initial['sub_unidade_destino'] = funcao.sub_unidade.id
                elif funcao.unidade:
                    self.initial['unidade_destino'] = funcao.unidade.id
                elif funcao.grande_comando:
                    self.initial['grande_comando_destino'] = funcao.grande_comando.id
                elif funcao.orgao:
                    self.initial['orgao_destino'] = funcao.orgao.id
    
    def clean(self):
        """Validação customizada do formulário"""
        cleaned_data = super().clean()
        tipo_entrada = cleaned_data.get('tipo_entrada')
        
        # Validar campos obrigatórios para doação
        if tipo_entrada == 'DOACAO':
            numero_processo = cleaned_data.get('numero_processo')
            numero_convenio = cleaned_data.get('numero_convenio')
            
            if not numero_processo:
                self.add_error('numero_processo', 'O número do processo é obrigatório para doações.')
            
            if not numero_convenio:
                self.add_error('numero_convenio', 'O número do convênio é obrigatório para doações.')
        
        return cleaned_data
        


class SaidaAlmoxarifadoForm(forms.ModelForm):
    """Formulário para registro de saída de materiais do almoxarifado"""
    
    class Meta:
        from .models import SaidaAlmoxarifado
        model = SaidaAlmoxarifado
        fields = [
            'produto', 'tipo_saida', 'data_saida', 'quantidade',
            'orgao_origem', 'grande_comando_origem', 'unidade_origem', 'sub_unidade_origem',
            'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino',
            'requisitante', 'responsavel_entrega', 'numero_requisicao', 'observacoes', 'ativo'
        ]
        widgets = {
            'produto': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'tipo_saida': forms.Select(attrs={'class': 'form-select'}),
            'data_saida': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_data_saida'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'orgao_origem': forms.Select(attrs={'class': 'form-select'}),
            'grande_comando_origem': forms.Select(attrs={'class': 'form-select'}),
            'unidade_origem': forms.Select(attrs={'class': 'form-select'}),
            'sub_unidade_origem': forms.Select(attrs={'class': 'form-select'}),
            'orgao_destino': forms.Select(attrs={'class': 'form-select'}),
            'grande_comando_destino': forms.Select(attrs={'class': 'form-select'}),
            'unidade_destino': forms.Select(attrs={'class': 'form-select'}),
            'sub_unidade_destino': forms.Select(attrs={'class': 'form-select'}),
            'requisitante': forms.Select(attrs={
                'class': 'form-select militar-select2',
                'data-placeholder': 'Digite o nome do militar...',
                'style': 'width: 100%;'
            }),
            'responsavel_entrega': forms.Select(attrs={'class': 'form-select'}),
            'numero_requisicao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da requisição'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Justificativa obrigatória para Baixa, Ajuste de Estoque e Outros...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Configurar queryset do item com filtro hierárquico
        from .models import ProdutoAlmoxarifado
        from .permissoes_militares import obter_sessao_ativa_usuario
        from .filtros_hierarquicos import aplicar_filtro_hierarquico_itens_almoxarifado
        
        queryset_item = ProdutoAlmoxarifado.objects.filter(ativo=True).order_by('codigo', 'descricao')
        
        # Aplicar filtro hierárquico se houver usuário e função
        if self.request and self.request.user:
            funcao_usuario = obter_sessao_ativa_usuario(self.request.user)
            if funcao_usuario:
                queryset_item = aplicar_filtro_hierarquico_itens_almoxarifado(queryset_item, funcao_usuario, self.request.user)
        
        self.fields['produto'].queryset = queryset_item
        
        # Tornar campos opcionais
        self.fields['produto'].required = False  # Múltiplos produtos são gerenciados via JavaScript
        self.fields['quantidade'].required = False  # Quantidade é calculada pelos itens
        self.fields['orgao_origem'].required = False
        self.fields['grande_comando_origem'].required = False
        self.fields['unidade_origem'].required = False
        self.fields['sub_unidade_origem'].required = False
        self.fields['orgao_destino'].required = False
        self.fields['grande_comando_destino'].required = False
        self.fields['unidade_destino'].required = False
        self.fields['sub_unidade_destino'].required = False
        self.fields['requisitante'].required = False
        self.fields['responsavel_entrega'].required = False
        
        # Esvaziar queryset do requisitante para permitir busca via AJAX no Select2
        from .models import Militar
        self.fields['requisitante'].queryset = Militar.objects.none()
        
        # Se estiver editando e já tiver requisitante, adicionar ao queryset
        if self.instance and self.instance.pk and self.instance.requisitante:
            self.fields['requisitante'].queryset = Militar.objects.filter(
                pk=self.instance.requisitante.pk
            )
        
        # Sobrescrever to_python para permitir valores vazios antes da validação do queryset
        original_to_python = self.fields['requisitante'].to_python
        
        def custom_to_python(value):
            # Se o valor estiver vazio, retornar None imediatamente
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                return None
            # Se for lista (FormData pode enviar arrays), pegar o primeiro elemento
            if isinstance(value, list):
                value = value[0] if value else ''
                if not value or value == '' or str(value).strip() == '':
                    return None
            # Se houver valor, processar normalmente
            return original_to_python(value)
        
        self.fields['requisitante'].to_python = custom_to_python
        
        # Se houver dados no POST e um ID de requisitante, adicionar ao queryset para validação
        if self.data and 'requisitante' in self.data:
            requisitante_id = self.data.get('requisitante', '')
            # Se for lista, pegar o primeiro elemento
            if isinstance(requisitante_id, list):
                requisitante_id = requisitante_id[0] if requisitante_id else ''
            requisitante_id = str(requisitante_id).strip()
            if requisitante_id and requisitante_id.isdigit():
                try:
                    militar = Militar.objects.filter(pk=int(requisitante_id), classificacao='ATIVO').first()
                    if militar:
                        # Adicionar o militar ao queryset para permitir validação
                        self.fields['requisitante'].queryset = Militar.objects.filter(pk=militar.pk)
                except (ValueError, TypeError):
                    pass
        
        # Preencher OM de origem com a OM da função do usuário (apenas na criação)
        if not self.instance.pk and self.request and self.request.user:
            from .permissoes_militares import obter_sessao_ativa_usuario
            sessao = obter_sessao_ativa_usuario(self.request.user)
            if sessao and sessao.funcao_militar_usuario:
                funcao = sessao.funcao_militar_usuario
                # Preencher com a OM mais específica disponível
                if funcao.sub_unidade:
                    self.initial['sub_unidade_origem'] = funcao.sub_unidade.id
                elif funcao.unidade:
                    self.initial['unidade_origem'] = funcao.unidade.id
                elif funcao.grande_comando:
                    self.initial['grande_comando_origem'] = funcao.grande_comando.id
                elif funcao.orgao:
                    self.initial['orgao_origem'] = funcao.orgao.id
        
        # Configurar observações como obrigatório para BAIXA, AJUSTE e OUTROS
        # Será validado no método clean()
        self.fields['observacoes'].required = False  # Será validado condicionalmente
        
        # Configurar data de saída
        if 'data_saida' in self.fields:
            self.fields['data_saida'].widget.format = '%Y-%m-%d'
            if not self.instance.pk:
                from datetime import date
                self.initial['data_saida'] = date.today().strftime('%Y-%m-%d')
            elif self.instance and self.instance.pk and self.instance.data_saida:
                try:
                    self.initial['data_saida'] = self.instance.data_saida.strftime('%Y-%m-%d')
                except:
                    pass
    
    def clean(self):
        """Validação customizada do formulário"""
        cleaned_data = super().clean()
        tipo_saida = cleaned_data.get('tipo_saida')
        observacoes = cleaned_data.get('observacoes')
        
        # Validar que observações seja obrigatório para BAIXA, AJUSTE e OUTROS
        if tipo_saida in ['BAIXA', 'AJUSTE', 'OUTROS']:
            if not observacoes or not observacoes.strip():
                raise forms.ValidationError({
                    'observacoes': 'Justificativa é obrigatória para Baixa, Ajuste de Estoque e Outros.'
                })
        
        return cleaned_data
    
    def clean_requisitante(self):
        """Garantir que campo vazio seja None"""
        # Pegar o valor diretamente dos dados do formulário para evitar erro de validação
        requisitante = self.data.get('requisitante', '')
        
        # Se vier como lista (FormData pode enviar arrays), pegar o primeiro elemento
        if isinstance(requisitante, list):
            requisitante = requisitante[0] if requisitante else ''
        
        # Se não estiver nos dados, tentar pegar do cleaned_data
        if not requisitante:
            requisitante = self.cleaned_data.get('requisitante', '')
        
        # Se for string vazia, None, ou não existir, retornar None
        if not requisitante or requisitante == '' or requisitante == 'None' or str(requisitante).strip() == '':
            return None
        
        # Se for um ID válido, verificar se o militar existe
        try:
            from .models import Militar
            # Converter para string e depois para int para garantir
            requisitante_str = str(requisitante).strip()
            if requisitante_str.isdigit():
                militar = Militar.objects.filter(pk=int(requisitante_str), classificacao='ATIVO').first()
                if militar:
                    return militar
            # Se já for uma instância de Militar, retornar diretamente
            elif isinstance(requisitante, Militar):
                return requisitante
        except (ValueError, TypeError, AttributeError) as e:
            # Se houver erro, retornar None (campo opcional)
            pass
        
        return None


class RequisicaoAlmoxarifadoForm(forms.ModelForm):
    """Formulário para criação de requisição de materiais entre OMs"""
    
    class Meta:
        from .models import RequisicaoAlmoxarifado
        model = RequisicaoAlmoxarifado
        fields = [
            # Campos legados 'item' e 'quantidade' removidos - agora usamos RequisicaoAlmoxarifadoProduto
            'orgao_requisitante', 'grande_comando_requisitante',
            'unidade_requisitante', 'sub_unidade_requisitante',
            'orgao_requisitada', 'grande_comando_requisitada', 
            'unidade_requisitada', 'sub_unidade_requisitada',
            'observacoes'
        ]
        widgets = {
            'orgao_requisitante': forms.Select(attrs={'class': 'form-select'}),
            'grande_comando_requisitante': forms.Select(attrs={'class': 'form-select'}),
            'unidade_requisitante': forms.Select(attrs={'class': 'form-select'}),
            'sub_unidade_requisitante': forms.Select(attrs={'class': 'form-select'}),
            'orgao_requisitada': forms.Select(attrs={'class': 'form-select'}),
            'grande_comando_requisitada': forms.Select(attrs={'class': 'form-select'}),
            'unidade_requisitada': forms.Select(attrs={'class': 'form-select'}),
            'sub_unidade_requisitada': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a requisição...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Campos legados 'item' e 'quantidade' removidos - múltiplos itens são gerenciados via RequisicaoAlmoxarifadoProduto
        
        # Tornar campos opcionais
        self.fields['orgao_requisitante'].required = False
        self.fields['grande_comando_requisitante'].required = False
        self.fields['unidade_requisitante'].required = False
        self.fields['sub_unidade_requisitante'].required = False
        self.fields['orgao_requisitada'].required = False
        self.fields['grande_comando_requisitada'].required = False
        self.fields['unidade_requisitada'].required = False
        self.fields['sub_unidade_requisitada'].required = False
        self.fields['observacoes'].required = False
        
        # IMPORTANTE: Se estiver editando (tem pk), garantir que os dados da instância sejam preservados
        # O Django ModelForm já faz isso automaticamente, mas vamos garantir que não sejam sobrescritos
        if self.instance and self.instance.pk:
            # Garantir que os valores da instância sejam usados
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'Formulário de edição - Requisição {self.instance.pk}')
            logger.info(f'  - Instância OM Requisitante: orgao={self.instance.orgao_requisitante_id}, grande_comando={self.instance.grande_comando_requisitante_id}, unidade={self.instance.unidade_requisitante_id}, sub_unidade={self.instance.sub_unidade_requisitante_id}')
            logger.info(f'  - Instância OM Requisitada: orgao={self.instance.orgao_requisitada_id}, grande_comando={self.instance.grande_comando_requisitada_id}, unidade={self.instance.unidade_requisitada_id}, sub_unidade={self.instance.sub_unidade_requisitada_id}')
            
            # Garantir que os campos tenham os valores da instância
            # O Django já faz isso, mas vamos garantir explicitamente
            if self.instance.orgao_requisitante_id:
                self.fields['orgao_requisitante'].initial = self.instance.orgao_requisitante_id
            if self.instance.grande_comando_requisitante_id:
                self.fields['grande_comando_requisitante'].initial = self.instance.grande_comando_requisitante_id
            if self.instance.unidade_requisitante_id:
                self.fields['unidade_requisitante'].initial = self.instance.unidade_requisitante_id
            if self.instance.sub_unidade_requisitante_id:
                self.fields['sub_unidade_requisitante'].initial = self.instance.sub_unidade_requisitante_id
            
            if self.instance.orgao_requisitada_id:
                self.fields['orgao_requisitada'].initial = self.instance.orgao_requisitada_id
            if self.instance.grande_comando_requisitada_id:
                self.fields['grande_comando_requisitada'].initial = self.instance.grande_comando_requisitada_id
            if self.instance.unidade_requisitada_id:
                self.fields['unidade_requisitada'].initial = self.instance.unidade_requisitada_id
            if self.instance.sub_unidade_requisitada_id:
                self.fields['sub_unidade_requisitada'].initial = self.instance.sub_unidade_requisitada_id
        
        # Preencher OM requisitante com a OM do usuário APENAS se for criação E não tiver dados na instância
        if self.request and self.request.user:
            from .permissoes_militares import obter_sessao_ativa_usuario
            sessao = obter_sessao_ativa_usuario(self.request.user)
            if sessao and sessao.funcao_militar_usuario:
                funcao = sessao.funcao_militar_usuario
                # Apenas para novas requisições (sem pk) E se a instância não tiver dados preenchidos
                if not self.instance.pk:  # Apenas para novas requisições
                    # Verificar se a instância já tem dados - se tiver, não sobrescrever
                    tem_dados_instancia = (
                        self.instance.orgao_requisitante or 
                        self.instance.grande_comando_requisitante or 
                        self.instance.unidade_requisitante or 
                        self.instance.sub_unidade_requisitante
                    )
                    
                    if not tem_dados_instancia:
                        # Só preencher se não houver dados na instância
                        if not self.initial.get('orgao_requisitante') and funcao.orgao:
                            self.initial['orgao_requisitante'] = funcao.orgao.id
                        if not self.initial.get('grande_comando_requisitante') and funcao.grande_comando:
                            self.initial['grande_comando_requisitante'] = funcao.grande_comando.id
                        if not self.initial.get('unidade_requisitante') and funcao.unidade:
                            self.initial['unidade_requisitante'] = funcao.unidade.id
                        if not self.initial.get('sub_unidade_requisitante') and funcao.sub_unidade:
                            self.initial['sub_unidade_requisitante'] = funcao.sub_unidade.id
    
    def clean(self):
        """Validação customizada do formulário"""
        try:
            cleaned_data = super().clean()
        except Exception as e:
            # Se houver erro no clean do super(), re-raise como ValidationError
            raise forms.ValidationError(f'Erro na validação: {str(e)}')
        
        # Validar que pelo menos um nível hierárquico da OM requisitada seja informado
        orgao_requisitada = cleaned_data.get('orgao_requisitada')
        grande_comando_requisitada = cleaned_data.get('grande_comando_requisitada')
        unidade_requisitada = cleaned_data.get('unidade_requisitada')
        sub_unidade_requisitada = cleaned_data.get('sub_unidade_requisitada')
        
        if not (orgao_requisitada or grande_comando_requisitada or unidade_requisitada or sub_unidade_requisitada):
            raise forms.ValidationError({
                'unidade_requisitada': 'É necessário informar pelo menos um nível hierárquico da OM requisitada.'
            })
        
        # Validar que a OM requisitada seja diferente da OM requisitante
        orgao_requisitante = cleaned_data.get('orgao_requisitante')
        grande_comando_requisitante = cleaned_data.get('grande_comando_requisitante')
        unidade_requisitante = cleaned_data.get('unidade_requisitante')
        sub_unidade_requisitante = cleaned_data.get('sub_unidade_requisitante')
        
        # Se a OM requisitante não foi preenchida, usar a OM do usuário
        if not (orgao_requisitante or grande_comando_requisitante or unidade_requisitante or sub_unidade_requisitante):
            if self.request and self.request.user:
                try:
                    from .permissoes_militares import obter_sessao_ativa_usuario
                    sessao = obter_sessao_ativa_usuario(self.request.user)
                    if sessao and sessao.funcao_militar_usuario:
                        funcao = sessao.funcao_militar_usuario
                        orgao_requisitante = funcao.orgao
                        grande_comando_requisitante = funcao.grande_comando
                        unidade_requisitante = funcao.unidade
                        sub_unidade_requisitante = funcao.sub_unidade
                except Exception:
                    # Se houver erro ao obter a sessão, ignorar e continuar
                    pass
        
        # Verificar se a OM requisitada é a mesma da OM requisitante
        # Comparar em todos os níveis hierárquicos para garantir que são diferentes
        # IMPORTANTE: Os valores podem ser objetos ou IDs, então precisamos normalizar
        mesma_om = False
        try:
            # Função auxiliar para obter ID de um valor (pode ser objeto ou ID)
            def get_id(value):
                if value is None:
                    return None
                if hasattr(value, 'id'):
                    return value.id
                return value
            
            # Comparar no nível mais específico primeiro (sub_unidade)
            sub_unidade_req_id = get_id(sub_unidade_requisitada)
            sub_unidade_reqte_id = get_id(sub_unidade_requisitante)
            if sub_unidade_req_id and sub_unidade_reqte_id:
                if sub_unidade_req_id == sub_unidade_reqte_id:
                    mesma_om = True
            
            # Se não tem sub_unidade, comparar unidade
            if not mesma_om:
                unidade_req_id = get_id(unidade_requisitada)
                unidade_reqte_id = get_id(unidade_requisitante)
                if unidade_req_id and unidade_reqte_id and not (sub_unidade_req_id or sub_unidade_reqte_id):
                    if unidade_req_id == unidade_reqte_id:
                        mesma_om = True
            
            # Se não tem unidade, comparar grande_comando
            if not mesma_om:
                gc_req_id = get_id(grande_comando_requisitada)
                gc_reqte_id = get_id(grande_comando_requisitante)
                if gc_req_id and gc_reqte_id and not (unidade_req_id or unidade_reqte_id or sub_unidade_req_id or sub_unidade_reqte_id):
                    if gc_req_id == gc_reqte_id:
                        mesma_om = True
            
            # Se não tem grande_comando, comparar orgao
            if not mesma_om:
                orgao_req_id = get_id(orgao_requisitada)
                orgao_reqte_id = get_id(orgao_requisitante)
                if orgao_req_id and orgao_reqte_id and not (gc_req_id or gc_reqte_id or unidade_req_id or unidade_reqte_id or sub_unidade_req_id or sub_unidade_reqte_id):
                    if orgao_req_id == orgao_reqte_id:
                        mesma_om = True
        except Exception as e:
            # Se houver erro na comparação, logar e continuar (não bloquear)
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Erro ao comparar OMs: {str(e)}')
            pass
        
        if mesma_om:
            raise forms.ValidationError({
                'unidade_requisitada': 'A OM requisitada deve ser diferente da OM requisitante. Para movimentações dentro da mesma OM, utilize Transferência.'
            })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Override do save para preencher automaticamente a OM requisitante se não foi preenchida"""
        requisicao = super().save(commit=False)
        
        # Apenas preencher OM requisitante se for uma nova requisição e não foi preenchida
        if not requisicao.pk and self.request and self.request.user:
            # Se a OM requisitante não foi preenchida, usar a OM do usuário
            if not (requisicao.orgao_requisitante or requisicao.grande_comando_requisitante or 
                    requisicao.unidade_requisitante or requisicao.sub_unidade_requisitante):
                try:
                    from .permissoes_militares import obter_sessao_ativa_usuario
                    sessao = obter_sessao_ativa_usuario(self.request.user)
                    if sessao and sessao.funcao_militar_usuario:
                        funcao = sessao.funcao_militar_usuario
                        # Preencher OM requisitante com a OM do usuário
                        requisicao.orgao_requisitante = funcao.orgao
                        requisicao.grande_comando_requisitante = funcao.grande_comando
                        requisicao.unidade_requisitante = funcao.unidade
                        requisicao.sub_unidade_requisitante = funcao.sub_unidade
                except Exception:
                    # Se houver erro, ignorar e continuar
                    pass
        
        if commit:
            requisicao.save()
        
        return requisicao


# ============================================================================
# FORMULÁRIOS PARA PROCESSOS ADMINISTRATIVOS
# ============================================================================

class ProcessoAdministrativoForm(forms.ModelForm):
    """Formulário para cadastro e edição de processos administrativos"""
    
    class Meta:
        model = ProcessoAdministrativo
        fields = [
            'numero', 'tipo', 'assunto', 'descricao', 'status', 'prioridade',
            'data_abertura', 'data_prazo', 'data_conclusao', 'data_arquivamento',
            'militares_envolvidos', 'militares_encarregados', 'escrivaos',
            'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'processo_origem', 'processo_procedimento',
            'observacoes', 'ativo'
        ]
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PA-2025-001',
                'style': 'text-transform: uppercase;'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'assunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Assunto ou título do processo'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descrição detalhada do processo...'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'data_abertura': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_prazo': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_conclusao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_arquivamento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'militares_envolvidos': forms.SelectMultiple(attrs={
                'class': 'form-select militar-select2-multiple',
                'multiple': 'multiple',
                'data-placeholder': 'Selecione os militares envolvidos'
            }),
            'militares_encarregados': forms.SelectMultiple(attrs={
                'class': 'form-select militar-select2-multiple',
                'multiple': 'multiple',
                'data-placeholder': 'Selecione os militares encarregados'
            }),
            'escrivaos': forms.SelectMultiple(attrs={
                'class': 'form-select militar-select2-multiple',
                'multiple': 'multiple',
                'data-placeholder': 'Selecione os escribões'
            }),
            'orgao': forms.Select(attrs={'class': 'form-select'}),
            'grande_comando': forms.Select(attrs={'class': 'form-select'}),
            'unidade': forms.Select(attrs={'class': 'form-select'}),
            'sub_unidade': forms.Select(attrs={'class': 'form-select'}),
            'processo_origem': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PA-2025-001'
            }),
            'processo_procedimento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PA-2025-001'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre o processo...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas militares ativos
        militares_ativos = Militar.objects.filter(classificacao='ATIVO').order_by('nome_completo')
        
        self.fields['militares_envolvidos'].queryset = militares_ativos
        self.fields['militares_encarregados'].queryset = militares_ativos
        self.fields['escrivaos'].queryset = militares_ativos
        
        # Tornar campos de organização opcionais
        self.fields['orgao'].required = False
        self.fields['grande_comando'].required = False
        self.fields['unidade'].required = False
        self.fields['sub_unidade'].required = False
        
        # Configurar datas
        if 'data_abertura' in self.fields:
            self.fields['data_abertura'].widget.format = '%Y-%m-%d'
            if not self.instance.pk:
                self.initial['data_abertura'] = date.today().strftime('%Y-%m-%d')
            elif self.instance.pk and self.instance.data_abertura:
                # Garantir que a data seja carregada no formato correto na edição
                self.initial['data_abertura'] = self.instance.data_abertura.strftime('%Y-%m-%d')
        
        if 'data_prazo' in self.fields and self.instance.pk and self.instance.data_prazo:
            self.initial['data_prazo'] = self.instance.data_prazo.strftime('%Y-%m-%d')
        
        if 'data_conclusao' in self.fields and self.instance.pk and self.instance.data_conclusao:
            self.initial['data_conclusao'] = self.instance.data_conclusao.strftime('%Y-%m-%d')
        
        if 'data_arquivamento' in self.fields and self.instance.pk and self.instance.data_arquivamento:
            self.initial['data_arquivamento'] = self.instance.data_arquivamento.strftime('%Y-%m-%d')
        
        # Configurar campos de processo relacionado (agora são campos de texto)
        if 'processo_origem' in self.fields:
            self.fields['processo_origem'].required = False
        
        if 'processo_procedimento' in self.fields:
            self.fields['processo_procedimento'].required = False


# ============================================================================
# FORMULÁRIOS PARA EQUIPAMENTOS OPERACIONAIS
# ============================================================================

class EquipamentoOperacionalForm(forms.ModelForm):
    """Formulário para cadastro e edição de equipamentos operacionais"""
    
    # Campo para seleção hierárquica do organograma (não é salvo diretamente)
    organograma_select = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'organograma-select'
        })
    )
    
    class Meta:
        model = EquipamentoOperacional
        fields = [
            'codigo', 'tipo', 'marca', 'modelo', 'numero_serie', 'ano_fabricacao',
            'horas_uso', 'status', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'observacoes', 'data_aquisicao', 'valor_aquisicao', 'fornecedor', 'ativo'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: EQ-001, BOMBA-01',
                'style': 'text-transform: uppercase;'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Honda, Yamaha, Briggs & Stratton'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: GX390, GX200'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de série do equipamento'
            }),
            'ano_fabricacao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1900',
                'max': '2100'
            }),
            'horas_uso': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'orgao': forms.HiddenInput(),
            'grande_comando': forms.HiddenInput(),
            'unidade': forms.HiddenInput(),
            'sub_unidade': forms.HiddenInput(),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observações sobre o equipamento...'
            }),
            'data_aquisicao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'valor_aquisicao': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_aquisicao',
                'placeholder': 'Digite o valor',
                'type': 'text'
            }),
            'fornecedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do fornecedor'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair request do kwargs se presente
        self.request = kwargs.pop('request', None)
        
        super().__init__(*args, **kwargs)
        # Tornar organizações não obrigatórias no formulário (validação será feita no model)
        self.fields['orgao'].required = False
        self.fields['grande_comando'].required = False
        self.fields['unidade'].required = False
        self.fields['sub_unidade'].required = False
        
        # Campos de organização ficam ocultos (serão preenchidos via JavaScript)
        self.fields['orgao'].widget = forms.HiddenInput()
        self.fields['grande_comando'].widget = forms.HiddenInput()
        self.fields['unidade'].widget = forms.HiddenInput()
        self.fields['sub_unidade'].widget = forms.HiddenInput()
        
        # Campo organograma_select não está no model, então precisa ser adicionado manualmente
        if 'organograma_select' not in self.fields:
            self.fields['organograma_select'] = forms.CharField(
                required=False,
                widget=forms.Select(attrs={
                    'class': 'form-select',
                    'id': 'organograma-select'
                })
            )
        
        # Tornar horas_uso somente leitura na edição (exceto para superusuários)
        if self.instance and self.instance.pk:  # Está editando um equipamento existente
            if not (self.request and self.request.user.is_superuser):
                # Tornar o campo somente leitura
                self.fields['horas_uso'].widget.attrs['readonly'] = True
                self.fields['horas_uso'].widget.attrs['class'] = 'form-control bg-light'
                self.fields['horas_uso'].required = False
        
        # Garantir que o campo de data de aquisição tenha o formato correto para input type="date"
        if 'data_aquisicao' in self.fields:
            # Configurar widget para formato ISO
            self.fields['data_aquisicao'].widget = forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_data_aquisicao'
            })
            self.fields['data_aquisicao'].widget.format = '%Y-%m-%d'
            
            # Se estiver editando e houver data, formatar corretamente
            if self.instance and self.instance.pk and self.instance.data_aquisicao:
                self.initial['data_aquisicao'] = self.instance.data_aquisicao.strftime('%Y-%m-%d')


class TempoUsoEquipamentoForm(forms.ModelForm):
    """Formulário para cadastro e edição de tempo de uso de equipamentos"""
    
    class Meta:
        model = TempoUsoEquipamento
        fields = [
            'equipamento', 'data_inicio', 'hora_inicio', 'data_fim', 'hora_fim',
            'horas_inicial', 'horas_final', 'operador', 'objetivo', 'local_uso',
            'observacoes', 'status'
        ]
        widgets = {
            'equipamento': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_equipamento'
            }),
            'data_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'data_fim': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'hora_fim': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'horas_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'horas_final': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'operador': forms.Select(attrs={
                'class': 'form-select militar-select2',
                'data-placeholder': 'Selecione o operador'
            }),
            'objetivo': forms.Select(attrs={'class': 'form-select'}),
            'local_uso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local onde o equipamento foi utilizado'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre o uso...'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        equipamento_id = kwargs.pop('equipamento_id', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas militares ativos
        militares_ativos = Militar.objects.filter(classificacao='ATIVO').order_by('nome_completo')
        self.fields['operador'].queryset = militares_ativos
        
        # Filtrar equipamentos ativos e disponíveis
        equipamentos = EquipamentoOperacional.objects.filter(ativo=True).order_by('codigo')
        self.fields['equipamento'].queryset = equipamentos
        
        # Se estiver editando um tempo de uso existente, definir o equipamento
        if self.instance and self.instance.pk:
            self.fields['equipamento'].widget.attrs['readonly'] = True
            self.fields['equipamento'].widget.attrs['disabled'] = True
        elif equipamento_id:
            # Se foi passado um equipamento_id, definir como inicial
            try:
                equipamento = EquipamentoOperacional.objects.get(pk=equipamento_id, ativo=True)
                self.initial['equipamento'] = equipamento
                # Preencher horas inicial com as horas de uso do equipamento
                self.initial['horas_inicial'] = float(equipamento.horas_uso)
            except EquipamentoOperacional.DoesNotExist:
                pass
        
        # Configurar datas
        if 'data_inicio' in self.fields:
            self.fields['data_inicio'].widget.format = '%Y-%m-%d'
            if not self.instance.pk:
                self.initial['data_inicio'] = date.today().strftime('%Y-%m-%d')
            elif self.instance.pk and self.instance.data_inicio:
                self.initial['data_inicio'] = self.instance.data_inicio.strftime('%Y-%m-%d')
        
        if 'data_fim' in self.fields and self.instance.pk and self.instance.data_fim:
            self.initial['data_fim'] = self.instance.data_fim.strftime('%Y-%m-%d')
        
        # Configurar horas
        if 'hora_inicio' in self.fields:
            if not self.instance.pk:
                from datetime import datetime
                self.initial['hora_inicio'] = datetime.now().strftime('%H:%M')
            elif self.instance.pk and self.instance.hora_inicio:
                self.initial['hora_inicio'] = self.instance.hora_inicio.strftime('%H:%M')
        
        if 'hora_fim' in self.fields and self.instance.pk and self.instance.hora_fim:
            self.initial['hora_fim'] = self.instance.hora_fim.strftime('%H:%M')


class EquipamentoTransferenciaForm(forms.ModelForm):
    """Formulário para transferência de equipamentos operacionais"""
    
    # Campo para seleção hierárquica do organograma de destino
    organograma_destino_select = forms.CharField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'organograma-destino-select'
        })
    )
    
    class Meta:
        model = TransferenciaEquipamento
        fields = [
            'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino',
            'justificativa', 'observacoes'
        ]
        widgets = {
            'orgao_destino': forms.HiddenInput(),
            'grande_comando_destino': forms.HiddenInput(),
            'unidade_destino': forms.HiddenInput(),
            'sub_unidade_destino': forms.HiddenInput(),
            'justificativa': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Justificativa para a transferência do equipamento...',
                'required': True
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais sobre a transferência...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Tornar organizações não obrigatórias no formulário (validação será feita no model)
        self.fields['orgao_destino'].required = False
        self.fields['grande_comando_destino'].required = False
        self.fields['unidade_destino'].required = False
        self.fields['sub_unidade_destino'].required = False
        
        # Campos de organização ficam ocultos (serão preenchidos via JavaScript)
        self.fields['orgao_destino'].widget = forms.HiddenInput()
        self.fields['grande_comando_destino'].widget = forms.HiddenInput()
        self.fields['unidade_destino'].widget = forms.HiddenInput()
        self.fields['sub_unidade_destino'].widget = forms.HiddenInput()
        
        # Campo organograma_destino_select não está no model, então precisa ser adicionado manualmente
        if 'organograma_destino_select' not in self.fields:
            self.fields['organograma_destino_select'] = forms.CharField(
                required=False,
                widget=forms.Select(attrs={
                    'class': 'form-select',
                    'id': 'organograma-destino-select'
                })
            )


class AbastecimentoEquipamentoForm(forms.ModelForm):
    """Formulário para cadastro e edição de abastecimentos de equipamentos operacionais"""
    
    class Meta:
        from .models import AbastecimentoEquipamento
        model = AbastecimentoEquipamento
        fields = [
            'equipamento', 'data_abastecimento', 'quantidade_litros', 'valor_litro', 
            'valor_total', 'horas_uso_abastecimento', 'tipo_combustivel', 'posto_fornecedor',
            'com_aditivos', 'tipo_aditivo', 'quantidade_aditivo', 'valor_unitario_aditivo',
            'valor_total_aditivo', 'valor_total_nota', 'responsavel', 'observacoes', 'ativo'
        ]
        widgets = {
            'equipamento': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'data_abastecimento': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'id': 'id_data_abastecimento'
            }),
            'quantidade_litros': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Ex: 50.00'
            }),
            'valor_litro': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_litro',
                'placeholder': 'Digite o valor',
                'type': 'text'
            }),
            'valor_total': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_total',
                'placeholder': 'Será calculado automaticamente',
                'readonly': True,
                'type': 'text'
            }),
            'horas_uso_abastecimento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Horas de uso no momento do abastecimento'
            }),
            'tipo_combustivel': forms.Select(attrs={'class': 'form-select'}),
            'posto_fornecedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do posto ou fornecedor'
            }),
            'com_aditivos': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_com_aditivos',
            }),
            'tipo_aditivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Aditivo para diesel, limpa bicos, etc.',
                'id': 'id_tipo_aditivo',
            }),
            'quantidade_aditivo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Quantidade',
                'id': 'id_quantidade_aditivo',
            }),
            'valor_unitario_aditivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Valor unitário',
                'type': 'text',
                'id': 'id_valor_unitario_aditivo',
            }),
            'valor_total_aditivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calculado automaticamente',
                'readonly': True,
                'type': 'text',
                'id': 'id_valor_total_aditivo',
            }),
            'valor_total_nota': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Soma automática',
                'readonly': True,
                'type': 'text',
                'id': 'id_valor_total_nota',
            }),
            'responsavel': forms.Select(attrs={
                'class': 'form-select militar-select2',
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre o abastecimento...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import EquipamentoOperacional, Militar
        
        # Filtrar apenas equipamentos ativos
        self.fields['equipamento'].queryset = EquipamentoOperacional.objects.filter(ativo=True).order_by('codigo')
        
        # Filtrar apenas militares ativos
        self.fields['responsavel'].queryset = Militar.objects.filter(ativo=True).order_by('posto_graduacao', 'nome_completo')


class ManutencaoEquipamentoForm(forms.ModelForm):
    """Formulário para cadastro e edição de manutenções de equipamentos operacionais"""
    
    class Meta:
        from .models import ManutencaoEquipamento
        model = ManutencaoEquipamento
        fields = [
            'equipamento', 'data_manutencao', 'tipo_manutencao', 'horas_uso_manutencao',
            'descricao_servico', 'fornecedor_oficina', 'valor_manutencao', 'pecas_trocadas',
            'proximas_horas_revisao', 'observacoes', 'responsavel', 'ativo'
        ]
        widgets = {
            'equipamento': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'data_manutencao': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'id': 'id_data_manutencao'
            }),
            'tipo_manutencao': forms.Select(attrs={'class': 'form-select'}),
            'horas_uso_manutencao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Horas de uso no momento da manutenção'
            }),
            'descricao_servico': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detalhamento dos serviços realizados...'
            }),
            'fornecedor_oficina': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da oficina ou fornecedor'
            }),
            'valor_manutencao': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_manutencao',
                'placeholder': 'Digite o valor',
                'type': 'text'
            }),
            'pecas_trocadas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lista de peças que foram substituídas...'
            }),
            'proximas_horas_revisao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Horas previstas para próxima revisão'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a manutenção...'
            }),
            'responsavel': forms.Select(attrs={
                'class': 'form-select militar-select2',
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import EquipamentoOperacional, Militar
        
        # Filtrar apenas equipamentos ativos
        self.fields['equipamento'].queryset = EquipamentoOperacional.objects.filter(ativo=True).order_by('codigo')
        
        # Filtrar apenas militares ativos
        self.fields['responsavel'].queryset = Militar.objects.filter(ativo=True).order_by('posto_graduacao', 'nome_completo')


class TrocaOleoEquipamentoForm(forms.ModelForm):
    """Formulário para cadastro e edição de trocas de óleo de equipamentos operacionais"""
    
    class Meta:
        from .models import TrocaOleoEquipamento
        model = TrocaOleoEquipamento
        fields = [
            'equipamento', 'data_troca', 'horas_uso_troca', 'tipo_oleo', 'nome_oleo',
            'quantidade_litros', 'valor_litro', 'valor_total', 'valor_total_nota',
            'fornecedor_oficina', 'trocou_filtro_oleo', 'valor_filtro_oleo',
            'outras_pecas', 'valor_outras_pecas', 'proximas_horas_troca',
            'responsavel', 'observacoes', 'ativo'
        ]
        widgets = {
            'equipamento': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'data_troca': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'id': 'id_data_troca'
            }),
            'horas_uso_troca': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Horas de uso no momento da troca'
            }),
            'tipo_oleo': forms.Select(attrs={'class': 'form-select'}),
            'nome_oleo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome/comercial do óleo utilizado'
            }),
            'quantidade_litros': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Ex: 5.00'
            }),
            'valor_litro': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_litro',
                'placeholder': 'Digite o valor',
                'type': 'text'
            }),
            'valor_total': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_total',
                'placeholder': 'Será calculado automaticamente',
                'readonly': True,
                'type': 'text'
            }),
            'valor_total_nota': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Soma automática',
                'readonly': True,
                'type': 'text',
                'id': 'id_valor_total_nota',
            }),
            'fornecedor_oficina': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da oficina ou fornecedor'
            }),
            'trocou_filtro_oleo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_trocou_filtro_oleo',
            }),
            'valor_filtro_oleo': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_filtro_oleo',
                'placeholder': 'Valor do filtro',
                'type': 'text'
            }),
            'outras_pecas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lista de outras peças trocadas (nome e valor)...'
            }),
            'valor_outras_pecas': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_valor_outras_pecas',
                'placeholder': 'Valor das outras peças',
                'type': 'text'
            }),
            'proximas_horas_troca': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Horas previstas para próxima troca'
            }),
            'responsavel': forms.Select(attrs={
                'class': 'form-select militar-select2',
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a troca de óleo...'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import EquipamentoOperacional, Militar
        
        # Filtrar apenas equipamentos ativos
        self.fields['equipamento'].queryset = EquipamentoOperacional.objects.filter(ativo=True).order_by('codigo')
        
        # Filtrar apenas militares ativos
        self.fields['responsavel'].queryset = Militar.objects.filter(ativo=True).order_by('posto_graduacao', 'nome_completo')
