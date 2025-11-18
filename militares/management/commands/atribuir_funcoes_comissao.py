#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from militares.models import FuncaoMilitar, UsuarioFuncaoMilitar, Orgao, GrandeComando, Unidade, SubUnidade


class Command(BaseCommand):
    help = 'Atribui funções de comissão aos usuários'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username do usuário')
        parser.add_argument('--funcao', type=str, help='Nome da função militar')
        parser.add_argument('--orgao', type=str, help='ID do órgão')
        parser.add_argument('--grande-comando', type=str, help='ID do grande comando')
        parser.add_argument('--unidade', type=str, help='ID da unidade')
        parser.add_argument('--sub-unidade', type=str, help='ID da sub-unidade')

    def handle(self, *args, **options):
        self.stdout.write('Atribuindo funções de comissão aos usuários...')
        
        # Listar funções de comissão disponíveis
        funcoes_comissao = FuncaoMilitar.objects.filter(grupo='COMISSAO', ativo=True)
        self.stdout.write('\nFunções de comissão disponíveis:')
        for funcao in funcoes_comissao:
            self.stdout.write(f'  {funcao.id}: {funcao.nome}')
        
        # Se não especificou usuário, listar usuários
        if not options['username']:
            self.stdout.write('\nUsuários disponíveis:')
            usuarios = User.objects.filter(is_active=True)
            for user in usuarios:
                self.stdout.write(f'  {user.username}: {user.get_full_name()}')
            return
        
        # Buscar usuário
        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuário {options["username"]} não encontrado!'))
            return
        
        # Buscar função
        if not options['funcao']:
            self.stdout.write(self.style.ERROR('Especifique a função com --funcao'))
            return
        
        try:
            funcao = FuncaoMilitar.objects.get(nome=options['funcao'])
        except FuncaoMilitar.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Função {options["funcao"]} não encontrada!'))
            return
        
        # Buscar lotação (opcional)
        orgao = None
        grande_comando = None
        unidade = None
        sub_unidade = None
        
        if options['orgao']:
            try:
                orgao = Orgao.objects.get(id=options['orgao'])
            except Orgao.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Órgão {options["orgao"]} não encontrado!'))
                return
        
        if options['grande_comando']:
            try:
                grande_comando = GrandeComando.objects.get(id=options['grande_comando'])
            except GrandeComando.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Grande Comando {options["grande_comando"]} não encontrado!'))
                return
        
        if options['unidade']:
            try:
                unidade = Unidade.objects.get(id=options['unidade'])
            except Unidade.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Unidade {options["unidade"]} não encontrada!'))
                return
        
        if options['sub_unidade']:
            try:
                sub_unidade = SubUnidade.objects.get(id=options['sub_unidade'])
            except SubUnidade.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Sub-Unidade {options["sub_unidade"]} não encontrada!'))
                return
        
        # Criar ou atualizar função militar do usuário
        funcao_usuario, created = UsuarioFuncaoMilitar.objects.get_or_create(
            usuario=user,
            funcao_militar=funcao,
            defaults={
                'orgao': orgao,
                'grande_comando': grande_comando,
                'unidade': unidade,
                'sub_unidade': sub_unidade,
                'ativo': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Função "{funcao.nome}" atribuída ao usuário {user.username}')
            )
        else:
            # Atualizar lotação se especificada
            if any([orgao, grande_comando, unidade, sub_unidade]):
                funcao_usuario.orgao = orgao
                funcao_usuario.grande_comando = grande_comando
                funcao_usuario.unidade = unidade
                funcao_usuario.sub_unidade = sub_unidade
                funcao_usuario.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Lotação atualizada para {user.username}')
                )
            else:
                self.stdout.write(f'  - Usuário {user.username} já possui a função {funcao.nome}')
        
        # Mostrar funções atuais do usuário
        self.stdout.write(f'\nFunções atuais de {user.username}:')
        funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(usuario=user, ativo=True)
        for funcao_usr in funcoes_usuario:
            lotacao = funcao_usr.get_nivel_lotacao()
            self.stdout.write(f'  - {funcao_usr.funcao_militar.nome} ({lotacao})')
