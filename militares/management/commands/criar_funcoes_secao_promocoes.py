#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from militares.models import FuncaoMilitar


class Command(BaseCommand):
    help = 'Cria funções militares para a Seção de Promoções'

    def handle(self, *args, **options):
        self.stdout.write('Criando funções militares para a Seção de Promoções...')
        
        # Funções da Seção de Promoções
        funcoes_secao = [
            {
                'nome': 'Chefe da Seção de Promoções',
                'descricao': 'Chefe responsável pela seção de promoções e fichas de conceito',
                'grupo': 'GESTAO',
                'nivel': 1,
                'acesso': 'TOTAL',
                'publicacao': 'EDITOR_GERAL',
                'ordem': 1,
                'ativo': True
            },
            {
                'nome': 'Auxiliar da Seção de Promoções',
                'descricao': 'Auxiliar da seção de promoções e fichas de conceito',
                'grupo': 'GESTAO',
                'nivel': 2,
                'acesso': 'DEPARTAMENTO',
                'publicacao': 'EDITOR',
                'ordem': 2,
                'ativo': True
            }
        ]
        
        criadas = 0
        for funcao_data in funcoes_secao:
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
