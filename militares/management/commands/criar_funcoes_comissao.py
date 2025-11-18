#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from militares.models import FuncaoMilitar


class Command(BaseCommand):
    help = 'Cria funções militares de comissão para o sistema de promoções'

    def handle(self, *args, **options):
        self.stdout.write('Criando funções militares de comissão...')
        
        # Funções de comissão para promoções
        funcoes_comissao = [
            {
                'nome': 'Presidente da Comissão de Promoções',
                'descricao': 'Presidente da comissão responsável por promoções',
                'grupo': 'COMISSAO',
                'nivel': 1,
                'acesso': 'TOTAL',
                'publicacao': 'EDITOR_GERAL',
                'ordem': 1,
                'ativo': True
            },
            {
                'nome': 'Membro Nato da Comissão de Promoções',
                'descricao': 'Membro nato da comissão de promoções',
                'grupo': 'COMISSAO',
                'nivel': 1,
                'acesso': 'TOTAL',
                'publicacao': 'EDITOR_GERAL',
                'ordem': 2,
                'ativo': True
            },
            {
                'nome': 'Membro da Comissão de Promoções',
                'descricao': 'Membro da comissão de promoções',
                'grupo': 'COMISSAO',
                'nivel': 2,
                'acesso': 'DEPARTAMENTO',
                'publicacao': 'EDITOR',
                'ordem': 3,
                'ativo': True
            },
            {
                'nome': 'Secretário da Comissão de Promoções',
                'descricao': 'Secretário da comissão de promoções',
                'grupo': 'COMISSAO',
                'nivel': 2,
                'acesso': 'DEPARTAMENTO',
                'publicacao': 'EDITOR',
                'ordem': 4,
                'ativo': True
            },
            {
                'nome': 'Relator da Comissão de Promoções',
                'descricao': 'Relator da comissão de promoções',
                'grupo': 'COMISSAO',
                'nivel': 3,
                'acesso': 'UNIDADE',
                'publicacao': 'DIGITADOR',
                'ordem': 5,
                'ativo': True
            }
        ]
        
        criadas = 0
        for funcao_data in funcoes_comissao:
            funcao, created = FuncaoMilitar.objects.get_or_create(
                nome=funcao_data['nome'],
                defaults=funcao_data
            )
            if created:
                criadas += 1
                self.stdout.write(f'  ✓ Criada: {funcao.nome}')
            else:
                self.stdout.write(f'  - Já existe: {funcao.nome}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Processo concluído! {criadas} funções criadas.')
        )
