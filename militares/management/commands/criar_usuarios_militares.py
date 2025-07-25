from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from militares.models import Militar

class Command(BaseCommand):
    help = 'Cria usuários do Django para todos os militares que ainda não possuem usuário vinculado (username = CPF)'

    def handle(self, *args, **options):
        total_criados = 0
        for militar in Militar.objects.filter(user__isnull=True):
            nomes = militar.nome_completo.strip().split()
            first_name = nomes[0]
            last_name = ' '.join(nomes[1:]) if len(nomes) > 1 else ''
            username = militar.cpf
            email = militar.email
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password='cbmepi123'
                )
                militar.user = user
                militar.save(update_fields=['user'])
                total_criados += 1
                self.stdout.write(self.style.SUCCESS(f'Usuário criado para {militar.nome_completo} (CPF: {militar.cpf})'))
            else:
                self.stdout.write(self.style.WARNING(f'Já existe usuário com username {username} (CPF: {militar.cpf})'))
        self.stdout.write(self.style.SUCCESS(f'Total de usuários criados: {total_criados}')) 