import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from militares.models import Militar


class Command(BaseCommand):
    help = 'Exporta militares para TSV compatível com importar_militares_csv'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='', help='Caminho do arquivo TSV de saída')

    def handle(self, *args, **options):
        output_path = options.get('file') or ''
        if not output_path:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            os.makedirs('backups', exist_ok=True)
            output_path = os.path.join('backups', f'militares_{ts}.csv')

        qs = Militar.objects.all().order_by('nome_completo')
        os.makedirs(os.path.dirname(output_path or '.'), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow([
                'matricula', 'nome_completo', 'nome_guerra', 'cpf', 'posto_graduacao', 'quadro',
                'numeracao_antiguidade', 'data_nascimento', 'data_ingresso', 'data_ultima_promocao',
                'email', 'telefone', 'celular', 'situacao', 'observacoes'
            ])

            for m in qs:
                posto = m.get_posto_graduacao_display() if m.posto_graduacao else ''
                quadro = m.get_quadro_display() if m.quadro else ''
                num_ant = m.numeracao_antiguidade if m.numeracao_antiguidade is not None else ''
                dn = m.data_nascimento.strftime('%d/%m/%Y') if m.data_nascimento else ''
                di = m.data_ingresso.strftime('%d/%m/%Y') if m.data_ingresso else ''
                dp = m.data_promocao_atual.strftime('%d/%m/%Y') if m.data_promocao_atual else ''
                situacao = 'ATIVO' if m.classificacao == 'ATIVO' else 'INATIVO'

                writer.writerow([
                    m.matricula or '',
                    m.nome_completo or '',
                    m.nome_guerra or '',
                    m.cpf or '',
                    posto,
                    quadro,
                    num_ant,
                    dn,
                    di,
                    dp,
                    m.email or '',
                    m.telefone or '',
                    m.celular or '',
                    situacao,
                    m.observacoes or ''
                ])

        self.stdout.write(self.style.SUCCESS(f'Exportado: {output_path}'))
