#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comando para sincronizar funções dos usuários com suas lotações atuais
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from militares.models import UsuarioFuncaoMilitar, Lotacao, FuncaoMilitar

class Command(BaseCommand):
    help = 'Sincroniza as funções dos usuários com suas lotações atuais'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Username específico para sincronizar (opcional)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem executar',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== SINCRONIZANDO FUNÇÕES COM LOTAÇÕES ==='))
        
        # Filtrar usuários
        if options['usuario']:
            usuarios = User.objects.filter(username=options['usuario'])
        else:
            usuarios = User.objects.filter(is_active=True)
        
        self.stdout.write(f'Total de usuários: {usuarios.count()}')
        
        for user in usuarios:
            if not hasattr(user, 'militar'):
                continue
                
            militar = user.militar
            self.stdout.write(f'\n👤 Processando: {user.username} - {militar.nome_guerra}')
            
            # Buscar lotação atual
            lotacao_atual = Lotacao.objects.filter(
                militar=militar,
                ativo=True,
                data_fim__isnull=True
            ).first()
            
            if not lotacao_atual:
                self.stdout.write(f'   ⚠️  Nenhuma lotação ativa encontrada')
                continue
                
            self.stdout.write(f'   🏢 Lotação: {lotacao_atual.lotacao}')
            self.stdout.write(f'   🏢 Unidade: {lotacao_atual.unidade}')
            
            # Buscar funções ativas do usuário
            funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
                usuario=user,
                ativo=True
            )
            
            self.stdout.write(f'   📋 Funções ativas: {funcoes_usuario.count()}')
            
            # Atualizar cada função com a lotação atual
            for funcao in funcoes_usuario:
                atualizado = False
                
                # Atualizar órgão se não estiver definido
                if not funcao.orgao and lotacao_atual.orgao:
                    if not options['dry_run']:
                        funcao.orgao = lotacao_atual.orgao
                    atualizado = True
                    self.stdout.write(f'     • Atualizando órgão: {lotacao_atual.orgao}')
                
                # Atualizar grande comando se não estiver definido
                if not funcao.grande_comando and lotacao_atual.grande_comando:
                    if not options['dry_run']:
                        funcao.grande_comando = lotacao_atual.grande_comando
                    atualizado = True
                    self.stdout.write(f'     • Atualizando grande comando: {lotacao_atual.grande_comando}')
                
                # Atualizar unidade se não estiver definida
                if not funcao.unidade and lotacao_atual.unidade:
                    if not options['dry_run']:
                        funcao.unidade = lotacao_atual.unidade
                    atualizado = True
                    self.stdout.write(f'     • Atualizando unidade: {lotacao_atual.unidade}')
                
                # Atualizar sub-unidade se não estiver definida
                if not funcao.sub_unidade and lotacao_atual.sub_unidade:
                    if not options['dry_run']:
                        funcao.sub_unidade = lotacao_atual.sub_unidade
                    atualizado = True
                    self.stdout.write(f'     • Atualizando sub-unidade: {lotacao_atual.sub_unidade}')
                
                if atualizado:
                    if not options['dry_run']:
                        funcao.save()
                    self.stdout.write(f'     ✅ Função "{funcao.funcao_militar.nome}" atualizada')
                else:
                    self.stdout.write(f'     ℹ️  Função "{funcao.funcao_militar.nome}" já está atualizada')
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\n⚠️  Modo dry-run: Nenhuma alteração foi feita'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Sincronização concluída!'))
