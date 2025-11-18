#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Formulários para gerenciar permissões de submenu integradas ao formulário de função militar
"""

from django import forms
from django.forms import inlineformset_factory
from .models import FuncaoMilitar, PermissaoSubmenu


class PermissaoSubmenuForm(forms.ModelForm):
    """Formulário para permissão de submenu individual"""
    
    class Meta:
        model = PermissaoSubmenu
        fields = ['submenu', 'acesso', 'ativo']
        widgets = {
            'submenu': forms.Select(attrs={
                'class': 'form-select permissao-submenu',
                'onchange': 'togglePermissao(this)'
            }),
            'acesso': forms.Select(attrs={
                'class': 'form-select permissao-acesso',
                'onchange': 'togglePermissao(this)'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input permissao-ativo',
                'onchange': 'togglePermissao(this)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar submenu e acesso obrigatórios apenas se ativo for True
        if not self.instance.pk or not self.instance.ativo:
            self.fields['submenu'].required = False
            self.fields['acesso'].required = False


class FuncaoMilitarComPermissoesForm(forms.ModelForm):
    """Formulário de função militar com permissões de submenu integradas"""
    
    class Meta:
        model = FuncaoMilitar
        fields = [
            'nome', 'acesso_sigilo', 'ordem', 'acesso', 'nivel', 
            'grupo', 'publicacao', 'descricao', 'ativo'
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
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição da função militar (opcional)'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            # Widgets para campos de menu
            'menu_dashboard': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_efetivo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_inativos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Submenus do Efetivo
            'menu_ativos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_transferir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_usuarios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_permissoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_fichas_oficiais': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_fichas_pracas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_quadros_acesso': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_quadros_fixacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_almanaques': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_promocoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_calendarios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_comissoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_meus_votos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_intersticios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_gerenciar_intersticios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_gerenciar_previsao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_administracao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_logs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_medalhas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_medalhas_concessoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_medalhas_propostas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_lotacoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_elegiveis': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_propostas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_notas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'menu_apenas_visualizacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Widgets para campos de permissão CRUD
            'fichas_oficiais_visualizar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fichas_oficiais_criar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fichas_oficiais_editar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fichas_oficiais_excluir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fichas_pracas_visualizar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fichas_pracas_criar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fichas_pracas_editar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fichas_pracas_excluir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quadros_acesso_visualizar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quadros_acesso_criar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quadros_acesso_editar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quadros_acesso_excluir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quadros_fixacao_visualizar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quadros_fixacao_criar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quadros_fixacao_editar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quadros_fixacao_excluir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'almanaques_visualizar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'almanaques_criar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'almanaques_editar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'almanaques_excluir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'promocoes_visualizar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'promocoes_criar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'promocoes_editar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'promocoes_excluir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'calendarios_visualizar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'calendarios_criar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'calendarios_editar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'calendarios_excluir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comissoes_visualizar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comissoes_criar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comissoes_editar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comissoes_excluir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'lotacoes_visualizar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'lotacoes_criar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'lotacoes_editar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'lotacoes_excluir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_gerenciar_usuarios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_gerenciar_permissoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_acessar_logs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pode_gerenciar_medalhas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].required = True
        self.fields['acesso_sigilo'].required = True
        self.fields['acesso'].required = True
        self.fields['nivel'].required = True
        self.fields['grupo'].required = True
        self.fields['publicacao'].required = True


# Formset para gerenciar permissões de submenu
PermissaoSubmenuFormSet = inlineformset_factory(
    FuncaoMilitar,
    PermissaoSubmenu,
    form=PermissaoSubmenuForm,
    extra=0,  # Não adicionar formulários extras automaticamente
    can_delete=True,
    fields=['submenu', 'acesso', 'ativo']
)


class ConfiguracaoPermissoesForm(forms.Form):
    """Formulário para configuração rápida de permissões"""
    
    CONFIGURACOES_CHOICES = [
        ('basico', 'Acesso Básico - Apenas Visualizar'),
        ('operacional', 'Acesso Operacional - Visualizar e Criar'),
        ('gerencial', 'Acesso Gerencial - Visualizar, Criar e Editar'),
        ('administrativo', 'Acesso Administrativo - Todas as permissões'),
        ('personalizado', 'Configuração Personalizada'),
    ]
    
    configuracao_tipo = forms.ChoiceField(
        choices=CONFIGURACOES_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
            'onchange': 'aplicarConfiguracao(this.value)'
        }),
        initial='personalizado',
        label='Tipo de Configuração'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['configuracao_tipo'].widget.attrs.update({
            'class': 'form-check-input configuracao-tipo'
        })


class PermissaoSubmenuBulkForm(forms.Form):
    """Formulário para configuração em lote de permissões"""
    
    submenus_selecionados = forms.MultipleChoiceField(
        choices=PermissaoSubmenu.SUBMENU_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input submenu-checkbox'
        }),
        required=False,
        label='Submenus'
    )
    
    acessos_selecionados = forms.MultipleChoiceField(
        choices=PermissaoSubmenu.ACESSO_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input acesso-checkbox'
        }),
        required=False,
        label='Tipos de Acesso'
    )
    
    acao = forms.ChoiceField(
        choices=[
            ('adicionar', 'Adicionar Permissões'),
            ('remover', 'Remover Permissões'),
            ('substituir', 'Substituir Todas as Permissões')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='adicionar',
        label='Ação'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS para estilização
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({
                    'class': 'form-check-input'
                })
