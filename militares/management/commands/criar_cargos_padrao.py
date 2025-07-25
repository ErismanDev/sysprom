from django.core.management.base import BaseCommand
from militares.models import CargoComissao


class Command(BaseCommand):
    help = 'Cria os cargos padrão da comissão'

    def handle(self, *args, **options):
        cargos_padrao = [
            {
                'nome': 'Comandante-Geral',
                'codigo': 'COMANDANTE_GERAL',
                'descricao': 'Comandante-Geral do Corpo de Bombeiros Militar',
                'ordem': 1
            },
            {
                'nome': 'Chefe do Estado Maior',
                'codigo': 'CHEFE_ESTADO_MAIOR',
                'descricao': 'Chefe do Estado Maior Geral',
                'ordem': 2
            },
            {
                'nome': 'Diretor de Pessoal',
                'codigo': 'DIRETOR_PESSOAL',
                'descricao': 'Diretor de Pessoal',
                'ordem': 3
            },
            {
                'nome': 'BM-1',
                'codigo': 'BM1',
                'descricao': 'Bombeiro Militar de 1ª Classe',
                'ordem': 4
            },
            {
                'nome': 'Oficial Superior',
                'codigo': 'OFICIAL_SUPERIOR',
                'descricao': 'Oficial Superior',
                'ordem': 5
            },
        ]

        for cargo_data in cargos_padrao:
            cargo, created = CargoComissao.objects.get_or_create(
                codigo=cargo_data['codigo'],
                defaults={
                    'nome': cargo_data['nome'],
                    'descricao': cargo_data['descricao'],
                    'ordem': cargo_data['ordem'],
                    'ativo': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Cargo criado: {cargo.nome}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Cargo já existe: {cargo.nome}')
                )

        self.stdout.write(
            self.style.SUCCESS('Cargos padrão criados com sucesso!')
        ) 