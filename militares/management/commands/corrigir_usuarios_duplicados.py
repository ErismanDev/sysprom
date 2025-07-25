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
    help = 'Corrige usuários duplicados, mantendo apenas os vinculados aos militares e corrigindo username para CPF'

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
            
            # Processar usuários duplicados
            self._processar_usuarios_duplicados(cpf_por_matricula, dry_run)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante o processamento: {str(e)}')
            )
            logger.error(f'Erro no processamento: {str(e)}', exc_info=True)

    def _processar_usuarios_duplicados(self, cpf_por_matricula, dry_run):
        """Processa usuários duplicados"""
        
        # Encontrar usuários duplicados por username
        from django.db.models import Count
        
        duplicados = User.objects.values('username').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        self.stdout.write(f'Encontrados {duplicados.count()} usernames duplicados')
        
        total_removidos = 0
        total_corrigidos = 0
        
        for dup in duplicados:
            username = dup['username']
            count = dup['count']
            
            self.stdout.write(f'Processando username: {username} ({count} ocorrências)')
            
            # Buscar todos os usuários com este username
            usuarios = User.objects.filter(username=username).order_by('id')
            
            # Encontrar o usuário vinculado ao militar
            usuario_vinculado = None
            usuarios_nao_vinculados = []
            
            for usuario in usuarios:
                if hasattr(usuario, 'militar') and usuario.militar:
                    usuario_vinculado = usuario
                else:
                    usuarios_nao_vinculados.append(usuario)
            
            if usuario_vinculado:
                self.stdout.write(f'  - Usuário vinculado encontrado: ID {usuario_vinculado.id}')
                
                # Corrigir username do usuário vinculado para CPF
                militar = usuario_vinculado.militar
                matricula = militar.matricula
                cpf = cpf_por_matricula.get(matricula, '')
                
                if cpf:
                    novo_username = cpf.replace('.', '').replace('-', '').replace(' ', '')
                    if novo_username != username:
                        if not dry_run:
                            # Verificar se o novo username já existe
                            if User.objects.filter(username=novo_username).exists():
                                self.stdout.write(
                                    self.style.WARNING(f'  - Username {novo_username} já existe, mantendo {username}')
                                )
                            else:
                                usuario_vinculado.username = novo_username
                                usuario_vinculado.save()
                                self.stdout.write(f'  - Username corrigido: {username} -> {novo_username}')
                                total_corrigidos += 1
                        else:
                            self.stdout.write(f'  - Username seria corrigido: {username} -> {novo_username}')
                            total_corrigidos += 1
                else:
                    self.stdout.write(f'  - CPF não encontrado para matrícula {matricula}')
                
                # Remover usuários não vinculados
                for usuario in usuarios_nao_vinculados:
                    if not dry_run:
                        usuario.delete()
                        self.stdout.write(f'  - Usuário removido: ID {usuario.id}')
                        total_removidos += 1
                    else:
                        self.stdout.write(f'  - Usuário seria removido: ID {usuario.id}')
                        total_removidos += 1
            else:
                self.stdout.write(f'  - Nenhum usuário vinculado encontrado para {username}')
                # Se não há usuário vinculado, manter apenas o primeiro
                for usuario in usuarios_nao_vinculados[1:]:
                    if not dry_run:
                        usuario.delete()
                        self.stdout.write(f'  - Usuário removido: ID {usuario.id}')
                        total_removidos += 1
                    else:
                        self.stdout.write(f'  - Usuário seria removido: ID {usuario.id}')
                        total_removidos += 1
        
        # Estatísticas finais
        self.stdout.write(
            self.style.SUCCESS(f'\nResumo:')
        )
        self.stdout.write(f'  - Usuários removidos: {total_removidos}')
        self.stdout.write(f'  - Usernames corrigidos: {total_corrigidos}')
        
        if not dry_run:
            total_usuarios = User.objects.count()
            usuarios_vinculados = User.objects.filter(militar__isnull=False).count()
            usuarios_nao_vinculados = User.objects.filter(militar__isnull=True).count()
            
            self.stdout.write(f'  - Total de usuários após correção: {total_usuarios}')
            self.stdout.write(f'  - Usuários vinculados: {usuarios_vinculados}')
            self.stdout.write(f'  - Usuários não vinculados: {usuarios_nao_vinculados}') 