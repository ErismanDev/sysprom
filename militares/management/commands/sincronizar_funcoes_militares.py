"""
Comando Django para sincronizar funções dos militares
"""

from django.core.management.base import BaseCommand
from militares.sincronizar_funcoes_militar import sincronizar_todos_militares


class Command(BaseCommand):
    help = 'Sincroniza as funções dos usuários com as funções exercidas dos militares'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Sincronizar apenas um usuário específico (username)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar detalhes da sincronização',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        usuario_especifico = options.get('usuario')
        
        if usuario_especifico:
            from django.contrib.auth.models import User
            from militares.sincronizar_funcoes_militar import sincronizar_funcoes_militar
            
            try:
                usuario = User.objects.get(username=usuario_especifico)
                resultado = sincronizar_funcoes_militar(usuario)
                
                if resultado['sucesso']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Sucesso para {usuario.username}: {resultado["mensagem"]}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Erro para {usuario.username}: {resultado["mensagem"]}'
                        )
                    )
                    
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Usuário {usuario_especifico} não encontrado')
                )
        else:
            # Sincronizar todos os militares
            self.stdout.write('Iniciando sincronização de todas as funções...')
            
            resultados = sincronizar_todos_militares()
            
            # Calcular estatísticas
            total_usuarios = len(resultados)
            sucessos = len([r for r in resultados if r['sucesso']])
            total_criadas = sum([r['funcoes_criadas'] for r in resultados])
            total_atualizadas = sum([r['funcoes_atualizadas'] for r in resultados])
            total_desativadas = sum([r.get('funcoes_desativadas', 0) for r in resultados])
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSincronização concluída!\n'
                    f'Usuários processados: {total_usuarios}\n'
                    f'Sucessos: {sucessos}\n'
                    f'Funções criadas: {total_criadas}\n'
                    f'Funções atualizadas: {total_atualizadas}\n'
                    f'Funções desativadas: {total_desativadas}'
                )
            )
            
            if verbose:
                self.stdout.write('\nDetalhes por usuário:')
                for resultado in resultados:
                    status = 'SUCCESS' if resultado['sucesso'] else 'ERROR'
                    self.stdout.write(
                        f'{status}: {resultado["usuario"]} - {resultado["mensagem"]}'
                    )

