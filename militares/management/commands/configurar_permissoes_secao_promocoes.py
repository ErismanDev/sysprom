#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para configurar automaticamente as permissões da Seção de Promoções
para as funções específicas: Chefe da Seção de Promoções, Diretor de Gestão de Pessoas,
e Auxiliar da Seção de Promoções.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from militares.models import FuncaoMilitar, PermissaoSubmenu


class Command(BaseCommand):
    help = 'Configura permissões da Seção de Promoções para funções específicas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove todas as permissões existentes antes de configurar',
        )
        parser.add_argument(
            '--funcao',
            type=str,
            help='Configura permissões apenas para uma função específica',
        )

    def handle(self, *args, **options):
        # Funções que devem ter acesso total à Seção de Promoções
        funcoes_secao_promocoes = [
            'Chefe da Seção de Promoções',
            'Diretor de Gestão de Pessoas',
            'Auxiliar da Seção de Promoções'
        ]
        
        # Se foi especificada uma função específica
        if options['funcao']:
            if options['funcao'] not in funcoes_secao_promocoes:
                raise CommandError(f'Função "{options["funcao"]}" não é válida. '
                                 f'Funções válidas: {", ".join(funcoes_secao_promocoes)}')
            funcoes_secao_promocoes = [options['funcao']]
        
        # Buscar as funções no banco de dados
        funcoes = FuncaoMilitar.objects.filter(nome__in=funcoes_secao_promocoes)
        
        if not funcoes.exists():
            self.stdout.write(
                self.style.WARNING('Nenhuma função encontrada. Verifique se as funções existem no sistema.')
            )
            return
        
        self.stdout.write(f'Configurando permissões para {len(funcoes)} função(ões)...')
        
        with transaction.atomic():
            for funcao in funcoes:
                self.stdout.write(f'Processando função: {funcao.nome}')
                
                # Remover permissões existentes se solicitado
                if options['reset']:
                    permissoes_removidas = PermissaoSubmenu.objects.filter(
                        funcao_militar=funcao
                    ).count()
                    PermissaoSubmenu.objects.filter(funcao_militar=funcao).delete()
                    self.stdout.write(f'  Removidas {permissoes_removidas} permissões existentes')
                
                # Criar perfil completo de permissões
                try:
                    PermissaoSubmenu.criar_perfil_secao_promocoes(funcao)
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Permissões configuradas com sucesso para {funcao.nome}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Erro ao configurar permissões para {funcao.nome}: {str(e)}')
                    )
                    raise CommandError(f'Erro ao configurar permissões: {str(e)}')
        
        # Mostrar resumo das permissões configuradas
        self.stdout.write('\n' + '='*50)
        self.stdout.write('RESUMO DAS PERMISSÕES CONFIGURADAS')
        self.stdout.write('='*50)
        
        for funcao in funcoes:
            permissoes = PermissaoSubmenu.obter_permissoes_funcao(funcao)
            self.stdout.write(f'\n{funcao.nome}:')
            self.stdout.write(f'  Total de permissões: {permissoes.count()}')
            
            # Agrupar por submenu
            submenus = {}
            for permissao in permissoes:
                submenu = permissao.get_submenu_display()
                if submenu not in submenus:
                    submenus[submenu] = []
                submenus[submenu].append(permissao.get_acesso_display())
            
            for submenu, acessos in submenus.items():
                self.stdout.write(f'    {submenu}: {", ".join(acessos)}')
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Configuração de permissões concluída com sucesso!')
        )
        
        # Instruções para o usuário
        self.stdout.write('\n' + '='*50)
        self.stdout.write('PRÓXIMOS PASSOS')
        self.stdout.write('='*50)
        self.stdout.write('1. Execute as migrações: python manage.py migrate')
        self.stdout.write('2. Reinicie o servidor Django')
        self.stdout.write('3. As permissões estarão ativas no sistema')
        self.stdout.write('4. Para gerenciar permissões individualmente, acesse o admin Django')
