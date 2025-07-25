from django.core.management.base import BaseCommand
from militares.models import CargoFuncao, UsuarioFuncao
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Cria uma função padrão para usuários que não conseguem fazer login'

    def handle(self, *args, **options):
        # Criar função padrão
        cargo_padrao, created = CargoFuncao.objects.get_or_create(
            nome='Administrador',
            defaults={
                'descricao': 'Função padrão para administradores do sistema',
                'ativo': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Função padrão "{cargo_padrao.nome}" criada com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Função "{cargo_padrao.nome}" já existe.')
            )
        
        # Verificar se há usuários sem função
        usuarios_sem_funcao = User.objects.filter(funcoes__isnull=True)
        
        for usuario in usuarios_sem_funcao:
            # Criar função para usuário
            UsuarioFuncao.objects.get_or_create(
                usuario=usuario,
                cargo_funcao=cargo_padrao,
                defaults={
                    'tipo_funcao': 'ADMINISTRATIVO',
                    'descricao': 'Função padrão atribuída automaticamente',
                    'status': 'ATIVO',
                    'data_inicio': '2024-01-01'
                }
            )
            self.stdout.write(
                self.style.SUCCESS(f'Função atribuída ao usuário {usuario.username}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Comando executado com sucesso!')
        ) 