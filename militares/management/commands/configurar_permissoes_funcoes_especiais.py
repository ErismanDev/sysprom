#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para configurar permissões das funções especiais da Seção de Promoções
"""

from django.core.management.base import BaseCommand
from militares.models import FuncaoMilitar


class Command(BaseCommand):
    help = 'Configura permissões das funções especiais da Seção de Promoções'

    def handle(self, *args, **options):
        # Funções que devem ter acesso total à Seção de Promoções
        funcoes_especiais = [
            'Chefe da Seção de Promoções',
            'Diretor de Gestão de Pessoas', 
            'Auxiliar da Seção de Promoções'
        ]
        
        # Módulos da Seção de Promoções
        modulos_secao = [
            'fichas_oficiais', 'fichas_pracas', 'quadros_acesso', 'quadros_fixacao',
            'almanaques', 'promocoes', 'calendarios', 'comissoes'
        ]
        
        # Ações CRUD
        acoes = ['visualizar', 'criar', 'editar', 'excluir']
        
        # Permissões especiais
        permissoes_especiais = [
            'pode_gerenciar_usuarios', 'pode_gerenciar_permissoes', 
            'pode_acessar_logs', 'pode_gerenciar_medalhas'
        ]
        
        for nome_funcao in funcoes_especiais:
            try:
                funcao = FuncaoMilitar.objects.get(nome=nome_funcao)
                self.stdout.write(f'Configurando permissões para: {nome_funcao}')
                
                # Ativar todos os menus da seção de promoções
                funcao.menu_fichas_oficiais = True
                funcao.menu_fichas_pracas = True
                funcao.menu_quadros_acesso = True
                funcao.menu_quadros_fixacao = True
                funcao.menu_almanaques = True
                funcao.menu_promocoes = True
                funcao.menu_calendarios = True
                funcao.menu_comissoes = True
                funcao.menu_meus_votos = True
                funcao.menu_intersticios = True
                funcao.menu_gerenciar_intersticios = True
                funcao.menu_gerenciar_previsao = True
                funcao.menu_lotacoes = True
                
                # Configurar permissões CRUD para todos os módulos
                for modulo in modulos_secao:
                    for acao in acoes:
                        campo = f"{modulo}_{acao}"
                        setattr(funcao, campo, True)
                
                # Configurar permissões especiais
                for permissao in permissoes_especiais:
                    setattr(funcao, permissao, True)
                
                # Salvar
                funcao.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Permissões configuradas para {nome_funcao}')
                )
                
            except FuncaoMilitar.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Função "{nome_funcao}" não encontrada')
                )
        
        self.stdout.write(
            self.style.SUCCESS('✓ Configuração de permissões concluída!')
        )
