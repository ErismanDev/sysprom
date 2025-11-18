from django import forms
from django.core.exceptions import ValidationError
from .models import SecaoPromocoes, Militar


class SecaoPromocoesForm(forms.ModelForm):
    """Formulário para Seção de Promoções"""
    
    class Meta:
        model = SecaoPromocoes
        fields = [
            'nome', 'sigla', 'descricao', 'status', 
            'chefe', 'auxiliar', 'observacoes'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Seção de Promoções de Oficiais'
            }),
            'sigla': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: SPPROM'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição da seção...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'chefe': forms.Select(attrs={
                'class': 'form-select'
            }),
            'auxiliar': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas militares ativos para chefe e auxiliar
        militares_ativos = Militar.objects.filter(situacao='ATIVO').order_by('nome_completo')
        self.fields['chefe'].queryset = militares_ativos
        self.fields['auxiliar'].queryset = militares_ativos
        
        # Tornar campos obrigatórios
        self.fields['nome'].required = True
        self.fields['sigla'].required = True
    
    def clean_sigla(self):
        sigla = self.cleaned_data.get('sigla')
        if sigla:
            sigla = sigla.upper().strip()
            
            # Verificar se já existe outra seção com a mesma sigla
            queryset = SecaoPromocoes.objects.filter(sigla=sigla)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError('Já existe uma seção com esta sigla.')
        
        return sigla
    
    def clean(self):
        cleaned_data = super().clean()
        chefe = cleaned_data.get('chefe')
        auxiliar = cleaned_data.get('auxiliar')
        
        # Verificar se chefe e auxiliar são diferentes
        if chefe and auxiliar and chefe == auxiliar:
            raise ValidationError('O chefe e o auxiliar devem ser pessoas diferentes.')
        
        return cleaned_data


class SecaoPromocoesSearchForm(forms.Form):
    """Formulário de busca para Seção de Promoções"""
    
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nome, sigla ou descrição...'
        }),
        label='Buscar'
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os Status')] + SecaoPromocoes.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Status'
    )
    
    chefe = forms.ModelChoiceField(
        queryset=Militar.objects.filter(situacao='ATIVO').order_by('nome_completo'),
        required=False,
        empty_label='Todos os Chefes',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Chefe'
    )
