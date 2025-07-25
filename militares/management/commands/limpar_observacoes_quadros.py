from django.core.management.base import BaseCommand
from militares.models import ItemQuadroFixacaoVagas


class Command(BaseCommand):
    help = 'Limpa observações antigas dos quadros de fixação de vagas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria alterado sem fazer as mudanças',
        )
        parser.add_argument(
            '--texto-padrao',
            type=str,
            default='Cópia fiel da previsão: Sem observações',
            help='Texto padrão a ser removido das observações',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        texto_padrao = options['texto_padrao']
        
        # Buscar itens com observações que contêm o texto padrão
        itens_com_observacoes_padrao = ItemQuadroFixacaoVagas.objects.filter(
            observacoes__icontains=texto_padrao
        )
        
        total_itens = itens_com_observacoes_padrao.count()
        
        if total_itens == 0:
            self.stdout.write(
                self.style.SUCCESS('Nenhum item encontrado com observações contendo o texto padrão.')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Encontrados {total_itens} itens com observações contendo o texto padrão.')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita.')
            )
            
            # Mostrar alguns exemplos
            for i, item in enumerate(itens_com_observacoes_padrao[:5]):
                self.stdout.write(
                    f'Item {item.id}: "{item.observacoes}" -> será limpo'
                )
            
            if total_itens > 5:
                self.stdout.write(f'... e mais {total_itens - 5} itens.')
        else:
            # Confirmar com o usuário
            confirmacao = input(
                f'\nTem certeza que deseja limpar as observações de {total_itens} itens? (s/N): '
            )
            
            if confirmacao.lower() != 's':
                self.stdout.write(
                    self.style.WARNING('Operação cancelada pelo usuário.')
                )
                return
            
            # Limpar as observações
            itens_atualizados = 0
            for item in itens_com_observacoes_padrao:
                if item.observacoes and texto_padrao in item.observacoes:
                    item.observacoes = ''  # Limpar completamente
                    item.save()
                    itens_atualizados += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Sucesso! {itens_atualizados} itens tiveram suas observações limpas.'
                )
            )
        
        # Mostrar estatísticas adicionais
        total_itens_com_observacoes = ItemQuadroFixacaoVagas.objects.filter(
            observacoes__isnull=False
        ).exclude(observacoes='').count()
        
        self.stdout.write(
            f'\nEstatísticas:\n'
            f'- Total de itens com observações não vazias: {total_itens_com_observacoes}\n'
            f'- Itens processados: {total_itens}'
        ) 