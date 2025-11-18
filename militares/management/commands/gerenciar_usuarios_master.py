#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from militares.models import UsuarioMaster
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Gerencia usuários master do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--listar',
            action='store_true',
            help='Lista todos os usuários master'
        )
        parser.add_argument(
            '--desativar',
            type=str,
            help='Desativa um usuário master pelo username'
        )
        parser.add_argument(
            '--ativar',
            type=str,
            help='Ativa um usuário master pelo username'
        )
        parser.add_argument(
            '--remover',
            type=str,
            help='Remove um usuário master pelo username'
        )
        parser.add_argument(
            '--info',
            type=str,
            help='Mostra informações detalhadas de um usuário master'
        )

    def handle(self, *args, **options):
        if options['listar']:
            self.listar_usuarios()
        elif options['desativar']:
            self.desativar_usuario(options['desativar'])
        elif options['ativar']:
            self.ativar_usuario(options['ativar'])
        elif options['remover']:
            self.remover_usuario(options['remover'])
        elif options['info']:
            self.mostrar_info(options['info'])
        else:
            self.stdout.write(
                self.style.ERROR('Use --help para ver as opções disponíveis')
            )

    def listar_usuarios(self):
        """Lista todos os usuários master"""
        usuarios = UsuarioMaster.objects.all().order_by('nome_completo')
        
        if not usuarios.exists():
            self.stdout.write(self.style.WARNING('Nenhum usuário master encontrado.'))
            return

        self.stdout.write(self.style.SUCCESS('Usuários Master:'))
        self.stdout.write('=' * 80)
        
        for usuario in usuarios:
            status = '✅ Ativo' if usuario.ativo else '❌ Inativo'
            ultimo_acesso = 'Nunca' if not usuario.data_ultimo_acesso else usuario.data_ultimo_acesso.strftime('%d/%m/%Y %H:%M')
            
            self.stdout.write(f'ID: {usuario.id}')
            self.stdout.write(f'Nome: {usuario.nome_completo}')
            self.stdout.write(f'Username: {usuario.username}')
            self.stdout.write(f'Email: {usuario.email}')
            self.stdout.write(f'Status: {status}')
            self.stdout.write(f'Último acesso: {ultimo_acesso}')
            self.stdout.write(f'Criado em: {usuario.data_criacao.strftime("%d/%m/%Y %H:%M")}')
            if usuario.observacoes:
                self.stdout.write(f'Observações: {usuario.observacoes}')
            self.stdout.write('-' * 80)

    def desativar_usuario(self, username):
        """Desativa um usuário master"""
        try:
            usuario = UsuarioMaster.objects.get(username=username)
            usuario.ativo = False
            usuario.save()
            
            # Também desativar o usuário Django
            try:
                user_django = User.objects.get(username=username)
                user_django.is_active = False
                user_django.save()
            except User.DoesNotExist:
                pass
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Usuário master "{username}" desativado com sucesso!')
            )
        except UsuarioMaster.DoesNotExist:
            raise CommandError(f'Usuário master "{username}" não encontrado!')

    def ativar_usuario(self, username):
        """Ativa um usuário master"""
        try:
            usuario = UsuarioMaster.objects.get(username=username)
            usuario.ativo = True
            usuario.save()
            
            # Também ativar o usuário Django
            try:
                user_django = User.objects.get(username=username)
                user_django.is_active = True
                user_django.save()
            except User.DoesNotExist:
                pass
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Usuário master "{username}" ativado com sucesso!')
            )
        except UsuarioMaster.DoesNotExist:
            raise CommandError(f'Usuário master "{username}" não encontrado!')

    def remover_usuario(self, username):
        """Remove um usuário master"""
        try:
            usuario = UsuarioMaster.objects.get(username=username)
            nome = usuario.nome_completo
            
            # Remover usuário master
            usuario.delete()
            
            # Também remover o usuário Django
            try:
                user_django = User.objects.get(username=username)
                user_django.delete()
            except User.DoesNotExist:
                pass
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Usuário master "{nome}" removido com sucesso!')
            )
        except UsuarioMaster.DoesNotExist:
            raise CommandError(f'Usuário master "{username}" não encontrado!')

    def mostrar_info(self, username):
        """Mostra informações detalhadas de um usuário master"""
        try:
            usuario = UsuarioMaster.objects.get(username=username)
            
            self.stdout.write(self.style.SUCCESS(f'Informações do Usuário Master: {usuario.nome_completo}'))
            self.stdout.write('=' * 60)
            self.stdout.write(f'ID: {usuario.id}')
            self.stdout.write(f'Nome completo: {usuario.nome_completo}')
            self.stdout.write(f'Username: {usuario.username}')
            self.stdout.write(f'Email: {usuario.email}')
            self.stdout.write(f'Status: {"✅ Ativo" if usuario.ativo else "❌ Inativo"}')
            self.stdout.write(f'Data de criação: {usuario.data_criacao.strftime("%d/%m/%Y %H:%M:%S")}')
            
            if usuario.data_ultimo_acesso:
                self.stdout.write(f'Último acesso: {usuario.data_ultimo_acesso.strftime("%d/%m/%Y %H:%M:%S")}')
            else:
                self.stdout.write('Último acesso: Nunca')
            
            if usuario.observacoes:
                self.stdout.write(f'Observações: {usuario.observacoes}')
            
            # Verificar se existe usuário Django correspondente
            try:
                user_django = User.objects.get(username=username)
                self.stdout.write(f'Usuário Django: ✅ Existe (ID: {user_django.id})')
                self.stdout.write(f'Superusuário Django: {"✅ Sim" if user_django.is_superuser else "❌ Não"}')
                self.stdout.write(f'Ativo Django: {"✅ Sim" if user_django.is_active else "❌ Não"}')
            except User.DoesNotExist:
                self.stdout.write('Usuário Django: ❌ Não existe')
                
        except UsuarioMaster.DoesNotExist:
            raise CommandError(f'Usuário master "{username}" não encontrado!')
