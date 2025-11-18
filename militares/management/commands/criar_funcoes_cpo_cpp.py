#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from militares.models import FuncaoMilitar


class Command(BaseCommand):
    help = 'Cria funções militares específicas para CPO e CPP'

    def handle(self, *args, **options):
        self.stdout.write('Criando funções militares específicas para CPO e CPP...')
        
        # Funções específicas para CPO (Comissão de Promoções de Oficiais)
        funcoes_cpo = [
            {
                'nome': 'Presidente da CPO',
                'descricao': 'Presidente da Comissão de Promoções de Oficiais',
                'grupo': 'COMISSAO',
                'nivel': 1,
                'acesso': 'TOTAL',
                'publicacao': 'EDITOR_GERAL',
                'ordem': 1,
                'ativo': True,
                'tipo_comissao': 'CPO'
            },
            {
                'nome': 'Membro Nato da CPO',
                'descricao': 'Membro nato da Comissão de Promoções de Oficiais',
                'grupo': 'COMISSAO',
                'nivel': 1,
                'acesso': 'TOTAL',
                'publicacao': 'EDITOR_GERAL',
                'ordem': 2,
                'ativo': True,
                'tipo_comissao': 'CPO'
            },
            {
                'nome': 'Membro Efetivo da CPO',
                'descricao': 'Membro efetivo da Comissão de Promoções de Oficiais',
                'grupo': 'COMISSAO',
                'nivel': 2,
                'acesso': 'DEPARTAMENTO',
                'publicacao': 'EDITOR',
                'ordem': 3,
                'ativo': True,
                'tipo_comissao': 'CPO'
            },
            {
                'nome': 'Secretário da CPO',
                'descricao': 'Secretário da Comissão de Promoções de Oficiais',
                'grupo': 'COMISSAO',
                'nivel': 2,
                'acesso': 'DEPARTAMENTO',
                'publicacao': 'EDITOR',
                'ordem': 4,
                'ativo': True,
                'tipo_comissao': 'CPO'
            },
            {
                'nome': 'Relator da CPO',
                'descricao': 'Relator da Comissão de Promoções de Oficiais',
                'grupo': 'COMISSAO',
                'nivel': 3,
                'acesso': 'UNIDADE',
                'publicacao': 'DIGITADOR',
                'ordem': 5,
                'ativo': True,
                'tipo_comissao': 'CPO'
            }
        ]
        
        # Funções específicas para CPP (Comissão de Promoções de Praças)
        funcoes_cpp = [
            {
                'nome': 'Presidente da CPP',
                'descricao': 'Presidente da Comissão de Promoções de Praças',
                'grupo': 'COMISSAO',
                'nivel': 1,
                'acesso': 'TOTAL',
                'publicacao': 'EDITOR_GERAL',
                'ordem': 1,
                'ativo': True,
                'tipo_comissao': 'CPP'
            },
            {
                'nome': 'Membro Nato da CPP',
                'descricao': 'Membro nato da Comissão de Promoções de Praças',
                'grupo': 'COMISSAO',
                'nivel': 1,
                'acesso': 'TOTAL',
                'publicacao': 'EDITOR_GERAL',
                'ordem': 2,
                'ativo': True,
                'tipo_comissao': 'CPP'
            },
            {
                'nome': 'Membro Efetivo da CPP',
                'descricao': 'Membro efetivo da Comissão de Promoções de Praças',
                'grupo': 'COMISSAO',
                'nivel': 2,
                'acesso': 'DEPARTAMENTO',
                'publicacao': 'EDITOR',
                'ordem': 3,
                'ativo': True,
                'tipo_comissao': 'CPP'
            },
            {
                'nome': 'Secretário da CPP',
                'descricao': 'Secretário da Comissão de Promoções de Praças',
                'grupo': 'COMISSAO',
                'nivel': 2,
                'acesso': 'DEPARTAMENTO',
                'publicacao': 'EDITOR',
                'ordem': 4,
                'ativo': True,
                'tipo_comissao': 'CPP'
            },
            {
                'nome': 'Relator da CPP',
                'descricao': 'Relator da Comissão de Promoções de Praças',
                'grupo': 'COMISSAO',
                'nivel': 3,
                'acesso': 'UNIDADE',
                'publicacao': 'DIGITADOR',
                'ordem': 5,
                'ativo': True,
                'tipo_comissao': 'CPP'
            }
        ]
        
        # Combinar todas as funções
        todas_funcoes = funcoes_cpo + funcoes_cpp
        
        criadas = 0
        for funcao_data in todas_funcoes:
            # Remover tipo_comissao dos dados antes de criar
            tipo_comissao = funcao_data.pop('tipo_comissao')
            
            funcao, created = FuncaoMilitar.objects.get_or_create(
                nome=funcao_data['nome'],
                defaults=funcao_data
            )
            if created:
                criadas += 1
                self.stdout.write(f'  ✓ Criada: {funcao.nome} ({tipo_comissao})')
            else:
                self.stdout.write(f'  - Já existe: {funcao.nome} ({tipo_comissao})')
        
        self.stdout.write(
            self.style.SUCCESS(f'Processo concluído! {criadas} funções criadas.')
        )
