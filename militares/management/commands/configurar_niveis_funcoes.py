#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from militares.models import FuncaoMilitar


class Command(BaseCommand):
    help = 'Configura os níveis hierárquicos das funções militares'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Resetar todos os níveis para 1',
        )

    def handle(self, *args, **options):
        self.stdout.write('=== CONFIGURAÇÃO DE NÍVEIS HIERÁRQUICOS ===\n')
        
        if options['reset']:
            self.stdout.write('Resetando todos os níveis para 1...')
            FuncaoMilitar.objects.all().update(nivel=1)
            self.stdout.write(self.style.SUCCESS('✅ Todos os níveis foram resetados para 1'))
            return
        
        # Configurações padrão de níveis por função
        configuracoes = {
            # TOTAL - Nível 5 (Master)
            'Administrador do Sistema': {'acesso': 'TOTAL', 'nivel': 5},
            'Administrador': {'acesso': 'TOTAL', 'nivel': 5},
            
            # ORGAO - Níveis 4-5
            'Comandante Geral': {'acesso': 'ORGAO', 'nivel': 5},
            'Subcomandante Geral': {'acesso': 'ORGAO', 'nivel': 4},
            'Chefe de Estado Maior': {'acesso': 'ORGAO', 'nivel': 4},
            'Inspetor Geral': {'acesso': 'ORGAO', 'nivel': 4},
            
            # GRANDE_COMANDO - Níveis 3-5
            'Comandante Regional': {'acesso': 'GRANDE_COMANDO', 'nivel': 5},
            'Subcomandante Regional': {'acesso': 'GRANDE_COMANDO', 'nivel': 4},
            'Chefe de Estado Maior Regional': {'acesso': 'GRANDE_COMANDO', 'nivel': 3},
            
            # UNIDADE - Níveis 2-5
            'Comandante de Unidade': {'acesso': 'UNIDADE', 'nivel': 5},
            'Subcomandante de Unidade': {'acesso': 'UNIDADE', 'nivel': 4},
            'Chefe de Estado Maior de Unidade': {'acesso': 'UNIDADE', 'nivel': 3},
            'Sargenteante': {'acesso': 'UNIDADE', 'nivel': 3},
            'Sargenteante Adjunto': {'acesso': 'UNIDADE', 'nivel': 2},
            
            # SUBUNIDADE - Níveis 1-5
            'Comandante de Subunidade': {'acesso': 'SUBUNIDADE', 'nivel': 5},
            'Subcomandante de Subunidade': {'acesso': 'SUBUNIDADE', 'nivel': 4},
            'Chefe de Seção': {'acesso': 'SUBUNIDADE', 'nivel': 3},
            'Sargenteante de Subunidade': {'acesso': 'SUBUNIDADE', 'nivel': 2},
            'Sargenteante Adjunto de Subunidade': {'acesso': 'SUBUNIDADE', 'nivel': 1},
            
            # FUNÇÕES ESPECIAIS
            'Serviço Operacional': {'acesso': 'UNIDADE', 'nivel': 1},
            'Usuário Padrão': {'acesso': 'SUBUNIDADE', 'nivel': 1},
        }
        
        # Aplicar configurações
        for nome_funcao, config in configuracoes.items():
            try:
                funcao = FuncaoMilitar.objects.get(nome=nome_funcao)
                funcao.acesso = config['acesso']
                funcao.nivel = config['nivel']
                funcao.save()
                
                self.stdout.write(
                    f'✅ {nome_funcao}: {config["acesso"]} - Nível {config["nivel"]}'
                )
            except FuncaoMilitar.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Função não encontrada: {nome_funcao}')
                )
        
        # Configurar funções restantes com níveis padrão
        funcoes_restantes = FuncaoMilitar.objects.filter(
            nome__in=[nome for nome in configuracoes.keys()]
        ).exclude(
            nome__in=[nome for nome in configuracoes.keys()]
        )
        
        for funcao in funcoes_restantes:
            # Determinar nível baseado no nome
            if 'comandante' in funcao.nome.lower():
                funcao.acesso = 'UNIDADE'
                funcao.nivel = 4
            elif 'sargenteante' in funcao.nome.lower():
                funcao.acesso = 'UNIDADE'
                funcao.nivel = 3
            elif 'chefe' in funcao.nome.lower():
                funcao.acesso = 'UNIDADE'
                funcao.nivel = 3
            else:
                funcao.acesso = 'SUBUNIDADE'
                funcao.nivel = 2
            
            funcao.save()
            self.stdout.write(
                f'✅ {funcao.nome}: {funcao.acesso} - Nível {funcao.nivel} (padrão)'
            )
        
        # Mostrar resumo
        self.stdout.write('\n=== RESUMO DOS NÍVEIS CONFIGURADOS ===')
        
        for acesso in ['TOTAL', 'ORGAO', 'GRANDE_COMANDO', 'UNIDADE', 'SUBUNIDADE']:
            funcoes = FuncaoMilitar.objects.filter(acesso=acesso).order_by('-nivel', 'nome')
            if funcoes.exists():
                self.stdout.write(f'\n{acesso}:')
                for funcao in funcoes:
                    self.stdout.write(f'  - {funcao.nome}: Nível {funcao.nivel}')
        
        self.stdout.write('\n✅ Configuração de níveis concluída!')
