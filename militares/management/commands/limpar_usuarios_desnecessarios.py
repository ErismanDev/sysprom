import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from militares.models import Militar
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Remove usuários desnecessários e corrige usernames dos militares para CPF'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa em modo de teste sem fazer alterações'
        )
        parser.add_argument(
            '--arquivo',
            type=str,
            default='Efetivo CBMEPI Atito SI Promoção 2.xlsx',
            help='Nome do arquivo Excel na pasta backup para obter CPFs'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        arquivo = options['arquivo']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DE TESTE - Nenhuma alteração será feita')
            )
        
        # Carregar dados do Excel para obter CPFs
        caminho_arquivo = os.path.join('backups', arquivo)
        if not os.path.exists(caminho_arquivo):
            self.stdout.write(
                self.style.ERROR(f'Arquivo não encontrado: {caminho_arquivo}')
            )
            return
        
        try:
            df = pd.read_excel(caminho_arquivo)
            self.stdout.write(f'Carregados {len(df)} registros do Excel')
            
            # Criar dicionário matricula -> cpf
            cpf_por_matricula = {}
            for index, row in df.iterrows():
                matricula = row.get('matricula', '')
                cpf = row.get('cpf', '')
                if pd.notna(matricula) and pd.notna(cpf):
                    cpf_por_matricula[str(matricula).strip()] = str(cpf).strip()
            
            self.stdout.write(f'Mapeamento criado: {len(cpf_por_matricula)} matrículas -> CPF')
            
            # Processar limpeza
            self._limpar_usuarios_desnecessarios(cpf_por_matricula, dry_run)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante o processamento: {str(e)}')
            )
            logger.error(f'Erro no processamento: {str(e)}', exc_info=True)

    def _limpar_usuarios_desnecessarios(self, cpf_por_matricula, dry_run):
        """Remove usuários desnecessários e corrige usernames"""
        
        # 1. Remover usuários sem militar vinculado
        usuarios_sem_militar = User.objects.filter(militar__isnull=True)
        total_usuarios_sem_militar = usuarios_sem_militar.count()
        
        self.stdout.write(f'Usuários sem militar vinculado: {total_usuarios_sem_militar}')
        
        if not dry_run:
            usuarios_sem_militar.delete()
            self.stdout.write(f'Removidos {total_usuarios_sem_militar} usuários sem militar')
        else:
            self.stdout.write(f'Seriam removidos {total_usuarios_sem_militar} usuários sem militar')
        
        # 2. Corrigir usernames dos militares para CPF
        militares_com_usuario = Militar.objects.filter(user__isnull=False)
        total_corrigidos = 0
        total_nao_encontrados = 0
        
        self.stdout.write(f'\nCorrigindo usernames dos militares...')
        
        for militar in militares_com_usuario:
            usuario = militar.user
            matricula = militar.matricula
            cpf = cpf_por_matricula.get(matricula, '')
            
            if cpf:
                novo_username = cpf.replace('.', '').replace('-', '').replace(' ', '')
                
                if novo_username != usuario.username:
                    if not dry_run:
                        # Verificar se o novo username já existe
                        if User.objects.filter(username=novo_username).exclude(id=usuario.id).exists():
                            self.stdout.write(
                                self.style.WARNING(f'  - Username {novo_username} já existe para {militar.nome_completo}, mantendo {usuario.username}')
                            )
                        else:
                            usuario.username = novo_username
                            usuario.save()
                            self.stdout.write(f'  - {militar.nome_completo}: {usuario.username} -> {novo_username}')
                            total_corrigidos += 1
                    else:
                        self.stdout.write(f'  - {militar.nome_completo}: {usuario.username} -> {novo_username}')
                        total_corrigidos += 1
            else:
                self.stdout.write(f'  - CPF não encontrado para {militar.nome_completo} (matrícula: {matricula})')
                total_nao_encontrados += 1
        
        # Estatísticas finais
        self.stdout.write(
            self.style.SUCCESS(f'\nResumo:')
        )
        self.stdout.write(f'  - Usuários removidos: {total_usuarios_sem_militar}')
        self.stdout.write(f'  - Usernames corrigidos: {total_corrigidos}')
        self.stdout.write(f'  - CPFs não encontrados: {total_nao_encontrados}')
        
        if not dry_run:
            total_usuarios = User.objects.count()
            usuarios_vinculados = User.objects.filter(militar__isnull=False).count()
            usuarios_nao_vinculados = User.objects.filter(militar__isnull=True).count()
            
            self.stdout.write(f'  - Total de usuários após limpeza: {total_usuarios}')
            self.stdout.write(f'  - Usuários vinculados: {usuarios_vinculados}')
            self.stdout.write(f'  - Usuários não vinculados: {usuarios_nao_vinculados}') 