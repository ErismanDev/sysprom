from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from militares.models import LogSistema


class Command(BaseCommand):
    help = 'Adiciona permissões necessárias para o sistema de logs'

    def handle(self, *args, **options):
        # Obter o content type do modelo LogSistema
        content_type = ContentType.objects.get_for_model(LogSistema)
        
        # Lista de permissões a serem criadas
        permissions = [
            ('view_logsistema', 'Can view log sistema'),
            ('add_logsistema', 'Can add log sistema'),
            ('change_logsistema', 'Can change log sistema'),
            ('delete_logsistema', 'Can delete log sistema'),
        ]
        
        created_count = 0
        for codename, name in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={'name': name}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Permissão criada: {codename}')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'Permissão já existe: {codename}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nProcesso concluído! {created_count} permissões criadas.')
        ) 