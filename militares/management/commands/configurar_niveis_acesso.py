#!/usr/bin/env python
from django.core.management.base import BaseCommand
from militares.models import UsuarioFuncaoMilitar, FuncaoMilitar


class Command(BaseCommand):
    help = 'Configura os níveis de acesso das funções militares baseado na hierarquia'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria alterado sem fazer as alterações',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita'))
        
        # Configurar níveis de acesso baseado no nome da função
        configuracoes = {
            'Administrador do Sistema': 'TOTAL',
            'Diretor de Gestão de Pessoas': 'TOTAL',
            'Chefe da Seção de Promoções': 'TOTAL',
            'Operador do Sistema': 'ORGAO',
            'CPO': 'UNIDADE',
            'CPP': 'UNIDADE',
            'Ajudante Geral': 'SUBUNIDADE',
            'Serviço Operacional': 'NENHUM',
        }
        
        total_atualizados = 0
        
        for nome_funcao, nivel_acesso in configuracoes.items():
            try:
                funcao = FuncaoMilitar.objects.get(nome=nome_funcao)
                
                # Buscar todas as funções de usuário com esta função militar
                funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
                    funcao_militar=funcao
                )
                
                count = funcoes_usuario.count()
                
                if count > 0:
                    if not dry_run:
                        funcoes_usuario.update(nivel_acesso=nivel_acesso)
                    
                    self.stdout.write(
                        f'{"[DRY-RUN] " if dry_run else ""}'
                        f'Função "{nome_funcao}": {count} registros atualizados para nível "{nivel_acesso}"'
                    )
                    total_atualizados += count
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Nenhum usuário encontrado com a função "{nome_funcao}"')
                    )
                    
            except FuncaoMilitar.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Função "{nome_funcao}" não encontrada')
                )
        
        # Configurar níveis baseado na lotação para funções não especificadas
        self.stdout.write('\nConfigurando níveis baseado na lotação...')
        
        funcoes_nao_configuradas = UsuarioFuncaoMilitar.objects.filter(
            nivel_acesso='NENHUM'
        ).exclude(
            funcao_militar__nome__in=configuracoes.keys()
        )
        
        for funcao_usuario in funcoes_nao_configuradas:
            nivel_sugerido = self._determinar_nivel_por_lotacao(funcao_usuario)
            
            if not dry_run:
                funcao_usuario.nivel_acesso = nivel_sugerido
                funcao_usuario.save()
            
            self.stdout.write(
                f'{"[DRY-RUN] " if dry_run else ""}'
                f'Usuário {funcao_usuario.usuario.username} - '
                f'Função "{funcao_usuario.funcao_militar.nome}": '
                f'nível sugerido "{nivel_sugerido}" baseado na lotação'
            )
            total_atualizados += 1
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\nDRY-RUN concluído. {total_atualizados} registros seriam atualizados.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nConfiguração concluída. {total_atualizados} registros atualizados.')
            )

    def _determinar_nivel_por_lotacao(self, funcao_usuario):
        """
        Determina o nível de acesso baseado na lotação do usuário
        """
        if funcao_usuario.orgao:
            return 'ORGAO'
        elif funcao_usuario.grande_comando:
            return 'GRANDE_COMANDO'
        elif funcao_usuario.unidade:
            return 'UNIDADE'
        elif funcao_usuario.sub_unidade:
            return 'SUBUNIDADE'
        else:
            return 'NENHUM'
