#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from militares.models import UsuarioFuncaoMilitar
from django.utils import timezone
from datetime import date


class Command(BaseCommand):
    help = 'Replica funções ativas para usuários, removendo funções antigas que não estão mais ativas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Username específico do usuário (opcional)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa em modo de teste sem fazer alterações',
        )
        parser.add_argument(
            '--forcar',
            action='store_true',
            help='Força a replicação mesmo se o usuário já tiver funções',
        )

    def handle(self, *args, **options):
        self.stdout.write("=== REPLICAÇÃO DE FUNÇÕES ATIVAS ===\n")
        
        # Buscar usuários
        if options['usuario']:
            try:
                usuarios = [User.objects.get(username=options['usuario'])]
                self.stdout.write(f"Processando usuário específico: {options['usuario']}")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Usuário {options["usuario"]} não encontrado!'))
                return
        else:
            usuarios = User.objects.filter(is_active=True)
            self.stdout.write(f"Processando {usuarios.count()} usuários ativos")
        
        # Buscar todas as funções ativas
        funcoes_ativas = CargoFuncao.objects.filter(ativo=True).order_by('nome')
        self.stdout.write(f"Encontradas {funcoes_ativas.count()} funções ativas no sistema\n")
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("MODO DRY-RUN: Nenhuma alteração será feita\n"))
        
        total_processados = 0
        total_funcoes_adicionadas = 0
        total_funcoes_removidas = 0
        
        for usuario in usuarios:
            self.stdout.write(f"Processando usuário: {usuario.username} ({usuario.get_full_name()})")
            
            # Buscar funções atuais do usuário
            funcoes_atuais = UsuarioFuncao.objects.filter(usuario=usuario)
            funcoes_atuais_ativas = funcoes_atuais.filter(status='ATIVO')
            
            self.stdout.write(f"  Funções atuais: {funcoes_atuais.count()} (ativas: {funcoes_atuais_ativas.count()})")
            
            # Se não forçar e usuário já tem funções, pular
            if not options['forcar'] and funcoes_atuais.exists():
                self.stdout.write(f"  ⚠ Pulando - usuário já possui funções (use --forcar para forçar)")
                continue
            
            # Remover funções antigas que não estão mais ativas no sistema
            funcoes_para_remover = funcoes_atuais.exclude(
                cargo_funcao__in=funcoes_ativas
            )
            
            if funcoes_para_remover.exists():
                self.stdout.write(f"  🗑 Removendo {funcoes_para_remover.count()} funções antigas:")
                for funcao in funcoes_para_remover:
                    self.stdout.write(f"    - {funcao.cargo_funcao.nome} (não está mais ativa no sistema)")
                    if not options['dry_run']:
                        funcao.delete()
                total_funcoes_removidas += funcoes_para_remover.count()
            
            # Adicionar funções ativas que o usuário não possui
            funcoes_para_adicionar = funcoes_ativas.exclude(
                id__in=funcoes_atuais.values_list('cargo_funcao_id', flat=True)
            )
            
            if funcoes_para_adicionar.exists():
                self.stdout.write(f"  ➕ Adicionando {funcoes_para_adicionar.count()} funções ativas:")
                for funcao in funcoes_para_adicionar:
                    self.stdout.write(f"    + {funcao.nome}")
                    if not options['dry_run']:
                        UsuarioFuncao.objects.create(
                            usuario=usuario,
                            cargo_funcao=funcao,
                            tipo_funcao='ADMINISTRATIVO',  # Tipo padrão
                            descricao=f'Função replicada automaticamente em {timezone.now().strftime("%d/%m/%Y")}',
                            status='ATIVO',
                            data_inicio=date.today()
                        )
                total_funcoes_adicionadas += funcoes_para_adicionar.count()
            else:
                self.stdout.write(f"  ✓ Usuário já possui todas as funções ativas")
            
            total_processados += 1
            self.stdout.write("")
        
        # Resumo
        self.stdout.write("=== RESUMO ===")
        self.stdout.write(f"Usuários processados: {total_processados}")
        self.stdout.write(f"Funções adicionadas: {total_funcoes_adicionadas}")
        self.stdout.write(f"Funções removidas: {total_funcoes_removidas}")
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("\n⚠ MODO DRY-RUN: Nenhuma alteração foi feita"))
            self.stdout.write("Execute sem --dry-run para aplicar as alterações")
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Replicação concluída com sucesso!"))
