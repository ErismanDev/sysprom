from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from militares.models import UsuarioFuncaoMilitar, FuncaoMilitar
from datetime import date
from django.db import transaction

class Command(BaseCommand):
    help = 'Migra o sistema de Cargos e Funções para Funções Militares'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a execução sem fazer alterações no banco de dados.',
        )
        parser.add_argument(
            '--remover-cargos',
            action='store_true',
            help='Remove os Cargos e Funções após a migração.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== MIGRAÇÃO PARA FUNÇÕES MILITARES ==='))
        dry_run = options['dry_run']
        remover_cargos = options['remover_cargos']

        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita'))

        # 1. Migrar todas as funções de usuário para funções militares
        self.stdout.write('\n1. Migrando funções de usuários...')
        
        funcoes_migradas = 0
        usuarios_processados = 0
        
        # Buscar função padrão "Serviço Operacional"
        funcao_servico = FuncaoMilitar.objects.filter(nome='Serviço Operacional', ativo=True).first()
        if not funcao_servico:
            self.stdout.write(self.style.ERROR('Função padrão "Serviço Operacional" não encontrada!'))
            return

        # Processar todos os usuários
        usuarios = User.objects.filter(is_active=True)
        
        for usuario in usuarios:
            usuarios_processados += 1
            
            # Verificar se já tem funções militares
            if UsuarioFuncaoMilitar.objects.filter(usuario=usuario).exists():
                self.stdout.write(f'  Usuário {usuario.username} já possui funções militares, pulando...')
                continue
            
            # Buscar funções do usuário (Cargos e Funções)
            funcoes_usuario = UsuarioFuncao.objects.filter(usuario=usuario)
            
            if funcoes_usuario.exists():
                # Migrar funções existentes
                for uf in funcoes_usuario:
                    # Buscar função militar equivalente
                    funcao_militar = FuncaoMilitar.objects.filter(
                        nome__iexact=uf.cargo_funcao.nome,
                        ativo=True
                    ).first()
                    
                    if not funcao_militar:
                        # Se não encontrar, usar função padrão
                        funcao_militar = funcao_servico
                        self.stdout.write(f'    Função "{uf.cargo_funcao.nome}" não encontrada, usando "Serviço Operacional"')
                    
                    if not dry_run:
                        UsuarioFuncaoMilitar.objects.get_or_create(
                            usuario=usuario,
                            funcao_militar=funcao_militar,
                            defaults={'ativo': uf.status == 'ATIVO'}
                        )
                    
                    funcoes_migradas += 1
                    self.stdout.write(f'    Migrada: {uf.cargo_funcao.nome} -> {funcao_militar.nome}')
            else:
                # Usuário sem funções, atribuir função padrão
                if not dry_run:
                    UsuarioFuncaoMilitar.objects.get_or_create(
                        usuario=usuario,
                        funcao_militar=funcao_servico,
                        defaults={'ativo': True}
                    )
                
                funcoes_migradas += 1
                self.stdout.write(f'    Atribuída função padrão: {usuario.username}')

        # 2. Remover Cargos e Funções se solicitado
        if remover_cargos and not dry_run:
            self.stdout.write('\n2. Removendo Cargos e Funções...')
            
            # Remover todas as funções de usuário
            funcoes_removidas = UsuarioFuncao.objects.count()
            UsuarioFuncao.objects.all().delete()
            self.stdout.write(f'  Removidas {funcoes_removidas} funções de usuário')
            
            # Cargos e funções já foram removidos do sistema
            self.stdout.write('  Cargos e funções já foram removidos do sistema')

        # 3. Estatísticas finais
        self.stdout.write('\n=== RESUMO ===')
        self.stdout.write(f'Usuários processados: {usuarios_processados}')
        self.stdout.write(f'Funções migradas: {funcoes_migradas}')
        
        if not dry_run:
            funcoes_militares_atuais = UsuarioFuncaoMilitar.objects.count()
            self.stdout.write(f'Total de funções militares ativas: {funcoes_militares_atuais}')
            
            if remover_cargos:
                self.stdout.write(self.style.SUCCESS('Sistema de Cargos e Funções removido com sucesso!'))
            else:
                self.stdout.write(self.style.SUCCESS('Migração concluída! Use --remover-cargos para remover o sistema antigo.'))
        else:
            self.stdout.write(self.style.WARNING('⚠ MODO DRY-RUN: Nenhuma alteração foi feita'))
            self.stdout.write(self.style.WARNING('Execute sem --dry-run para aplicar as alterações'))
