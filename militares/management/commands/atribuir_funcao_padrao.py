#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from militares.models import UsuarioFuncaoMilitar
from datetime import date


class Command(BaseCommand):
    help = 'Atribui a função padrão "Serviço Operacional" para usuários sem função específica'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa em modo de teste sem fazer alterações',
        )
        parser.add_argument(
            '--forcar',
            action='store_true',
            help='Força a atribuição mesmo para usuários que já possuem funções',
        )

    def handle(self, *args, **options):
        self.stdout.write("=== ATRIBUIÇÃO DE FUNÇÃO PADRÃO ===\n")
        
        # Buscar função padrão
        cargo_padrao = CargoFuncao.objects.filter(
            nome='Serviço Operacional',
            ativo=True
        ).first()
        
        if not cargo_padrao:
            self.stdout.write(self.style.ERROR('Função padrão "Serviço Operacional" não encontrada!'))
            return
        
        self.stdout.write(f"Função padrão encontrada: {cargo_padrao.nome}")
        
        # Buscar usuários sem funções
        if options['forcar']:
            usuarios = User.objects.filter(is_active=True)
            self.stdout.write("Modo forçado: processando todos os usuários ativos")
        else:
            usuarios = User.objects.filter(funcoes__isnull=True, is_active=True)
            self.stdout.write(f"Processando {usuarios.count()} usuários sem funções")
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("MODO DRY-RUN: Nenhuma alteração será feita\n"))
        
        total_processados = 0
        total_atribuidas = 0
        
        for usuario in usuarios:
            # Verificar se já possui funções (se não forçar)
            if not options['forcar'] and UsuarioFuncao.objects.filter(usuario=usuario).exists():
                continue
            
            self.stdout.write(f"Processando usuário: {usuario.username} ({usuario.get_full_name()})")
            
            # Verificar se já possui a função padrão
            funcao_existente = UsuarioFuncao.objects.filter(
                usuario=usuario,
                cargo_funcao=cargo_padrao
            ).first()
            
            if funcao_existente:
                self.stdout.write(f"  ✓ Já possui função padrão")
            else:
                self.stdout.write(f"  ➕ Atribuindo função padrão")
                if not options['dry_run']:
                    UsuarioFuncao.objects.create(
                        usuario=usuario,
                        cargo_funcao=cargo_padrao,
                        tipo_funcao='OPERACIONAL',
                        descricao='Função padrão atribuída automaticamente',
                        status='ATIVO',
                        data_inicio=date.today(),
                        observacoes='Função padrão para usuários sem função específica'
                    )
                total_atribuidas += 1
            
            total_processados += 1
        
        # Resumo
        self.stdout.write("\n=== RESUMO ===")
        self.stdout.write(f"Usuários processados: {total_processados}")
        self.stdout.write(f"Funções atribuídas: {total_atribuidas}")
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("\n⚠ MODO DRY-RUN: Nenhuma alteração foi feita"))
            self.stdout.write("Execute sem --dry-run para aplicar as alterações")
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Atribuição de função padrão concluída com sucesso!"))
