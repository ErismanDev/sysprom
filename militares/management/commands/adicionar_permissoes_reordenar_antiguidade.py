#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para adicionar permissões de reordenação de antiguidade
para as funções: Operador do Sistema, Administrador e Administrador do Sistema
"""

from django.core.management.base import BaseCommand
from militares.models import PermissaoFuncao


class Command(BaseCommand):
    help = 'Adiciona permissões de reordenação de antiguidade para funções específicas'

    def handle(self, *args, **options):
        """Execute o comando"""
        
        # Funções que devem ter permissão para reordenar antiguidade
        funcoes_permitidas = [
            'Diretor de Gestão de Pessoas',
            'Chefe da Seção de Promoções',
            'Operador do Sistema',
            'Administrador do Sistema'
        ]
        
        permissoes_criadas = 0
        permissoes_existentes = 0
        
        for nome_funcao in funcoes_permitidas:
            try:
                cargo_funcao = CargoFuncao.objects.get(nome=nome_funcao)
                
                # Verificar se a permissão já existe
                permissao_existe = PermissaoFuncao.objects.filter(
                    cargo_funcao=cargo_funcao,
                    modulo='MILITARES',
                    acesso='REORDENAR_ANTIGUIDADE'
                ).exists()
                
                if not permissao_existe:
                    # Criar a permissão
                    PermissaoFuncao.objects.create(
                        cargo_funcao=cargo_funcao,
                        modulo='MILITARES',
                        acesso='REORDENAR_ANTIGUIDADE',
                        observacoes=f'Permite {cargo_funcao.nome} reordenar antiguidade de militares',
                        ativo=True
                    )
                    permissoes_criadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Permissão REORDENAR_ANTIGUIDADE criada para {cargo_funcao.nome}'
                        )
                    )
                else:
                    permissoes_existentes += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Permissão REORDENAR_ANTIGUIDADE já existe para {cargo_funcao.nome}'
                        )
                    )
                    
            except CargoFuncao.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Função {nome_funcao} não encontrada no sistema'
                    )
                )
        
        # Resumo final
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== RESUMO ==='))
        self.stdout.write(f'Permissões criadas: {permissoes_criadas}')
        self.stdout.write(f'Permissões já existentes: {permissoes_existentes}')
        self.stdout.write('')
        
        if permissoes_criadas > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    'Permissões de reordenação de antiguidade configuradas com sucesso!'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Nenhuma permissão nova foi criada. Todas já existiam.'
                )
            )
