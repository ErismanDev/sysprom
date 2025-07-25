from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from militares.models import NotificacaoSessao


class Command(BaseCommand):
    help = 'Limpa notificações antigas do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Número de dias para considerar notificação como antiga (padrão: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra quantas notificações seriam removidas sem realmente removê-las'
        )

    def handle(self, *args, **options):
        dias = options['dias']
        dry_run = options['dry_run']
        
        data_limite = timezone.now() - timedelta(days=dias)
        
        # Buscar notificações antigas e lidas
        notificacoes_antigas = NotificacaoSessao.objects.filter(
            data_criacao__lt=data_limite,
            lida=True
        )
        
        count = notificacoes_antigas.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: {count} notificação(ões) antiga(s) seriam removida(s) '
                    f'(mais antigas que {dias} dias)'
                )
            )
        else:
            notificacoes_antigas.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'{count} notificação(ões) antiga(s) removida(s) com sucesso'
                )
            )
        
        # Mostrar estatísticas
        total_notificacoes = NotificacaoSessao.objects.count()
        notificacoes_nao_lidas = NotificacaoSessao.objects.filter(lida=False).count()
        
        self.stdout.write(
            self.style.INFO(
                f'Estatísticas: {total_notificacoes} total, {notificacoes_nao_lidas} não lidas'
            )
        ) 