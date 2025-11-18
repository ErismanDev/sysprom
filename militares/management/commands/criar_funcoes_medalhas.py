from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from militares.models import UsuarioFuncaoMilitar


class Command(BaseCommand):
    help = 'Garante as funções Ajudante Geral e Comandante Geral e permite atribuí-las a usuários por username'

    def add_arguments(self, parser):
        parser.add_argument('--ajudante', nargs='*', help='Usernames para receber função Ajudante Geral')
        parser.add_argument('--comandante', nargs='*', help='Usernames para receber função Comandante Geral')

    def handle(self, *args, **options):
        cargos = {
            'Ajudante Geral': {
                'descricao': 'Função com acesso ao módulo de Medalhas',
                'tipo_funcao': 'ADMINISTRATIVO',
            },
            'Comandante Geral': {
                'descricao': 'Função com acesso ao módulo de Medalhas',
                'tipo_funcao': 'ADMINISTRATIVO',
            },
        }

        for nome, meta in cargos.items():
            cargo, created = FuncaoMilitar.objects.get_or_create(
                nome=nome,
                defaults={
                    'descricao': meta['descricao'],
                    'ativo': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Criado cargo/função: {nome}'))
            else:
                self.stdout.write(self.style.WARNING(f'Cargo já existe: {nome}'))

        # Atribuir por username, se fornecido
        for flag, cargo_nome in [(options.get('ajudante'), 'Ajudante Geral'), (options.get('comandante'), 'Comandante Geral')]:
            if not flag:
                continue
            cargo = FuncaoMilitar.objects.get(nome=cargo_nome)
            for username in flag:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Usuário não encontrado: {username}'))
                    continue
                UsuarioFuncao.objects.get_or_create(
                    usuario=user,
                    cargo_funcao=cargo,
                    defaults={
                        'tipo_funcao': 'ADMINISTRATIVO',
                        'descricao': 'Função atribuída via comando criar_funcoes_medalhas',
                        'status': 'ATIVO',
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Função "{cargo_nome}" atribuída a {username}'))

        self.stdout.write(self.style.SUCCESS('Concluído.'))


