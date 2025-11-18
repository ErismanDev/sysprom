from django.core.management.base import BaseCommand
from militares.models import FuncaoMilitar


class Command(BaseCommand):
    help = 'Configura os menus padrão para todas as funções militares baseado no grupo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Resetar todas as configurações de menu para os padrões do grupo',
        )

    def handle(self, *args, **options):
        self.stdout.write('Configurando menus para funções militares...')
        
        funcoes = FuncaoMilitar.objects.filter(ativo=True)
        total = funcoes.count()
        configuradas = 0
        resetadas = 0
        
        for funcao in funcoes:
            if options['reset']:
                # Resetar para configurações padrão do grupo
                self._configurar_por_grupo(funcao)
                resetadas += 1
                self.stdout.write(f'  ✓ Resetada: {funcao.nome}')
            else:
                # Apenas configurar se não tiver configuração
                if not hasattr(funcao, 'menu_config') or not funcao.menu_config:
                    self._configurar_por_grupo(funcao)
                    configuradas += 1
                    self.stdout.write(f'  ✓ Configurada: {funcao.nome}')
                else:
                    self.stdout.write(f'  - Já configurada: {funcao.nome}')
        
        if options['reset']:
            self.stdout.write(
                self.style.SUCCESS(f'Processo concluído! {resetadas} funções resetadas.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Processo concluído! {configuradas} funções configuradas de {total} total.')
            )

    def _configurar_por_grupo(self, funcao):
        """Configura os menus baseado no grupo da função"""
        
        # Configurações baseadas no grupo da função
        if funcao.grupo == 'ADMINISTRATIVO':
            # Funções administrativas têm acesso total
            funcao.menu_dashboard = True
            funcao.menu_efetivo = True
            funcao.menu_inativos = True
            funcao.menu_usuarios = True
            funcao.menu_permissoes = True
            funcao.menu_fichas_oficiais = True
            funcao.menu_fichas_pracas = True
            funcao.menu_quadros_acesso = True
            funcao.menu_quadros_fixacao = True
            funcao.menu_almanaques = True
            funcao.menu_promocoes = True
            funcao.menu_calendarios = True
            funcao.menu_comissoes = True
            funcao.menu_meus_votos = True
            funcao.menu_intersticios = True
            funcao.menu_gerenciar_intersticios = True
            funcao.menu_gerenciar_previsao = True
            funcao.menu_administracao = True
            funcao.menu_logs = True
            funcao.menu_medalhas = True
            funcao.menu_lotacoes = True
            funcao.menu_apenas_visualizacao = False
            
        elif funcao.grupo == 'GESTAO':
            # Funções de gestão têm acesso a promoções e administração limitada
            funcao.menu_dashboard = True
            funcao.menu_efetivo = True
            funcao.menu_inativos = True
            funcao.menu_usuarios = True
            funcao.menu_permissoes = True
            funcao.menu_fichas_oficiais = True
            funcao.menu_fichas_pracas = True
            funcao.menu_quadros_acesso = True
            funcao.menu_quadros_fixacao = True
            funcao.menu_almanaques = True
            funcao.menu_promocoes = True
            funcao.menu_calendarios = True
            funcao.menu_comissoes = True
            funcao.menu_meus_votos = True
            funcao.menu_intersticios = True
            funcao.menu_gerenciar_intersticios = True
            funcao.menu_gerenciar_previsao = True
            funcao.menu_administracao = True
            funcao.menu_logs = True
            funcao.menu_medalhas = True
            funcao.menu_lotacoes = True
            funcao.menu_apenas_visualizacao = False
            
        elif funcao.grupo == 'COMISSAO':
            # Funções de comissão têm acesso restrito apenas à seção de promoções
            funcao.menu_dashboard = True
            funcao.menu_efetivo = False
            funcao.menu_inativos = False
            funcao.menu_usuarios = False
            funcao.menu_permissoes = False
            funcao.menu_fichas_oficiais = True
            funcao.menu_fichas_pracas = True
            funcao.menu_quadros_acesso = True
            funcao.menu_quadros_fixacao = True
            funcao.menu_almanaques = True
            funcao.menu_promocoes = True
            funcao.menu_calendarios = True
            funcao.menu_comissoes = True
            funcao.menu_meus_votos = True
            funcao.menu_intersticios = True
            funcao.menu_gerenciar_intersticios = True
            funcao.menu_gerenciar_previsao = True
            funcao.menu_administracao = False
            funcao.menu_logs = False
            funcao.menu_medalhas = False
            funcao.menu_lotacoes = False
            funcao.menu_apenas_visualizacao = True
            
        else:
            # Outras funções têm acesso básico
            funcao.menu_dashboard = True
            funcao.menu_efetivo = True
            funcao.menu_inativos = True
            funcao.menu_usuarios = False
            funcao.menu_permissoes = False
            funcao.menu_fichas_oficiais = False
            funcao.menu_fichas_pracas = False
            funcao.menu_quadros_acesso = False
            funcao.menu_quadros_fixacao = False
            funcao.menu_almanaques = True
            funcao.menu_promocoes = False
            funcao.menu_calendarios = False
            funcao.menu_comissoes = False
            funcao.menu_meus_votos = False
            funcao.menu_intersticios = False
            funcao.menu_gerenciar_intersticios = False
            funcao.menu_gerenciar_previsao = False
            funcao.menu_administracao = False
            funcao.menu_logs = False
            funcao.menu_medalhas = True
            funcao.menu_lotacoes = True
            funcao.menu_apenas_visualizacao = False
        
        funcao.save()
