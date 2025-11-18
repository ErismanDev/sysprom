#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from militares.models import UsuarioMaster
from django.utils import timezone
import getpass


class Command(BaseCommand):
    help = 'Cria um usuário master com acesso total ao sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nome de usuário para o usuário master',
            required=True
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email para o usuário master',
            required=True
        )
        parser.add_argument(
            '--nome-completo',
            type=str,
            help='Nome completo do usuário master',
            required=True
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Senha para o usuário master (se não informada, será solicitada)',
            required=False
        )
        parser.add_argument(
            '--observacoes',
            type=str,
            help='Observações sobre o usuário master',
            required=False,
            default=''
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        nome_completo = options['nome_completo']
        password = options['password']
        observacoes = options['observacoes']

        # Verificar se o usuário master já existe
        if UsuarioMaster.objects.filter(username=username).exists():
            raise CommandError(f'Usuário master com username "{username}" já existe!')

        if UsuarioMaster.objects.filter(email=email).exists():
            raise CommandError(f'Usuário master com email "{email}" já existe!')

        # Solicitar senha se não foi fornecida
        if not password:
            password = getpass.getpass('Digite a senha para o usuário master: ')
            password_confirm = getpass.getpass('Confirme a senha: ')
            
            if password != password_confirm:
                raise CommandError('As senhas não coincidem!')

        try:
            # Criar usuário Django
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nome_completo.split(' ')[0] if ' ' in nome_completo else nome_completo,
                last_name=' '.join(nome_completo.split(' ')[1:]) if ' ' in nome_completo else '',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )

            # Criar usuário master
            usuario_master = UsuarioMaster.objects.create(
                username=username,
                email=email,
                nome_completo=nome_completo,
                observacoes=observacoes,
                ativo=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Usuário master "{nome_completo}" criado com sucesso!\n'
                    f'   Username: {username}\n'
                    f'   Email: {email}\n'
                    f'   ID: {usuario_master.id}\n'
                    f'   Data de criação: {usuario_master.data_criacao.strftime("%d/%m/%Y %H:%M:%S")}'
                )
            )

            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  IMPORTANTE:\n'
                    '   - Este usuário tem acesso total ao sistema\n'
                    '   - Não precisa de função militar ou lotação\n'
                    '   - Pode acessar todas as funcionalidades\n'
                    '   - Use com cuidado e responsabilidade'
                )
            )

        except Exception as e:
            # Se houve erro, remover o usuário Django se foi criado
            if 'user' in locals():
                user.delete()
            raise CommandError(f'Erro ao criar usuário master: {str(e)}')

    def listar_usuarios_master(self):
        """Lista todos os usuários master existentes"""
        usuarios = UsuarioMaster.objects.all()
        
        if not usuarios.exists():
            self.stdout.write(self.style.WARNING('Nenhum usuário master encontrado.'))
            return

        self.stdout.write(self.style.SUCCESS('Usuários Master existentes:'))
        for usuario in usuarios:
            status = '✅ Ativo' if usuario.ativo else '❌ Inativo'
            self.stdout.write(
                f'   {usuario.nome_completo} ({usuario.username}) - {status}'
            )
