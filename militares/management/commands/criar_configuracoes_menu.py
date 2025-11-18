"""
Comando Django para criar configurações de menu padrão para funções
"""

from django.core.management.base import BaseCommand
from militares.models import FuncaoMilitar, FuncaoMenuConfig


class Command(BaseCommand):
    help = 'Cria configurações de menu padrão para funções que não possuem'

    def add_arguments(self, parser):
        parser.add_argument(
            '--funcao-id',
            type=int,
            help='Criar configuração para uma função específica',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostrar o que seria criado, sem fazer alterações',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        funcao_id = options.get('funcao_id')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Modo DRY-RUN: Nenhuma alteração será feita')
            )
        
        if funcao_id:
            # Criar configuração para função específica
            try:
                funcao = FuncaoMilitar.objects.get(id=funcao_id)
                self.criar_configuracao_funcao(funcao, dry_run)
            except FuncaoMilitar.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Função com ID {funcao_id} não encontrada')
                )
        else:
            # Criar configurações para todas as funções sem configuração
            funcoes_sem_config = FuncaoMilitar.objects.filter(
                menu_config__isnull=True
            )
            
            self.stdout.write(f'Funções sem configuração: {funcoes_sem_config.count()}')
            
            for funcao in funcoes_sem_config:
                self.criar_configuracao_funcao(funcao, dry_run)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Configurações de menu criadas!')
        )
    
    def criar_configuracao_funcao(self, funcao, dry_run=False):
        """Cria configuração de menu para uma função específica"""
        self.stdout.write(f'🔧 Processando: {funcao.nome} ({funcao.get_grupo_display()})')
        
        if dry_run:
            self.stdout.write(f'   [DRY-RUN] Configuração seria criada')
            return
        
        # Verificar se já existe configuração
        if FuncaoMenuConfig.objects.filter(funcao_militar=funcao).exists():
            self.stdout.write(f'   ⚠️  Configuração já existe')
            return
        
        # Criar configuração baseada no grupo
        config = FuncaoMenuConfig.objects.create(
            funcao_militar=funcao,
            show_dashboard=True,  # Dashboard sempre visível
        )
        
        # Configurações baseadas no grupo
        if funcao.grupo == 'ADMINISTRATIVO':
            self.configurar_administrativo(config)
        elif funcao.grupo == 'OPERACIONAL':
            self.configurar_operacional(config)
        elif funcao.grupo == 'COMISSAO':
            self.configurar_comissao(config)
        elif funcao.grupo == 'GESTAO':
            self.configurar_gestao(config)
        else:
            self.configurar_padrao(config)
        
        config.save()
        self.stdout.write(f'   ✅ Configuração criada')
    
    def configurar_administrativo(self, config):
        """Configuração para funções administrativas"""
        config.show_efetivo = True
        config.show_inativos = True
        config.show_usuarios = True
        config.show_permissoes = True
        config.show_secao_promocoes = True
        config.show_fichas_oficiais = True
        config.show_fichas_pracas = True
        config.show_quadros_acesso = True
        config.show_quadros_fixacao = True
        config.show_almanaques = True
        config.show_promocoes = True
        config.show_calendarios = True
        config.show_comissoes = True
        config.show_meus_votos = True
        config.show_intersticios = True
        config.show_gerenciar_intersticios = True
        config.show_gerenciar_previsao = True
        config.show_administracao = True
        config.show_logs = True
        config.show_medalhas = True
        config.show_lotacoes = True
        config.is_consultor = False
    
    def configurar_operacional(self, config):
        """Configuração para funções operacionais"""
        config.show_efetivo = True
        config.show_ativos = True
        config.show_inativos = True
        config.show_lotacoes = True
        config.show_medalhas = True
        config.is_consultor = False
    
    def configurar_comissao(self, config):
        """Configuração para funções de comissão"""
        config.show_secao_promocoes = True
        config.show_fichas_oficiais = True
        config.show_fichas_pracas = True
        config.show_quadros_acesso = True
        config.show_quadros_fixacao = True
        config.show_comissoes = True
        config.show_meus_votos = True
        config.show_medalhas = True
        config.is_consultor = True
    
    def configurar_gestao(self, config):
        """Configuração para funções de gestão"""
        config.show_efetivo = True
        config.show_ativos = True
        config.show_inativos = True
        config.show_lotacoes = True
        config.show_medalhas = True
        config.show_secao_promocoes = True
        config.show_fichas_oficiais = True
        config.show_fichas_pracas = True
        config.show_quadros_acesso = True
        config.show_quadros_fixacao = True
        config.show_comissoes = True
        config.show_meus_votos = True
        config.is_consultor = False
    
    def configurar_padrao(self, config):
        """Configuração padrão (mínima)"""
        config.show_efetivo = False
        config.show_ativos = False
        config.show_inativos = False
        config.show_lotacoes = False
        config.show_medalhas = False
        config.show_secao_promocoes = False
        config.show_fichas_oficiais = False
        config.show_fichas_pracas = False
        config.show_quadros_acesso = False
        config.show_quadros_fixacao = False
        config.show_comissoes = False
        config.show_meus_votos = False
        config.is_consultor = True
