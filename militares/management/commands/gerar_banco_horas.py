from django.core.management.base import BaseCommand
from django.db import transaction
from militares.models import EscalaMilitar, BancoHoras


class Command(BaseCommand):
    help = 'Gera movimentações no banco de horas baseadas nas escalas existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-inicio',
            type=str,
            help='Data de início para processar escalas (formato: YYYY-MM-DD)',
        )
        parser.add_argument(
            '--data-fim',
            type=str,
            help='Data de fim para processar escalas (formato: YYYY-MM-DD)',
        )
        parser.add_argument(
            '--militar-id',
            type=int,
            help='ID do militar específico para processar',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar no banco de dados',
        )

    def handle(self, *args, **options):
        from datetime import datetime, date
        
        data_inicio = options.get('data_inicio')
        data_fim = options.get('data_fim')
        militar_id = options.get('militar_id')
        dry_run = options.get('dry_run', False)
        
        # Construir query
        escalas_militares = EscalaMilitar.objects.select_related('militar', 'escala')
        
        if data_inicio:
            escalas_militares = escalas_militares.filter(escala__data__gte=data_inicio)
        
        if data_fim:
            escalas_militares = escalas_militares.filter(escala__data__lte=data_fim)
        
        if militar_id:
            escalas_militares = escalas_militares.filter(militar_id=militar_id)
        
        # Filtrar apenas escalas aprovadas ou ativas
        escalas_militares = escalas_militares.filter(
            escala__status__in=['aprovada', 'ativa']
        )
        
        total_escalas = escalas_militares.count()
        self.stdout.write(f'Processando {total_escalas} escalas de militares...')
        
        if dry_run:
            self.stdout.write('MODO DRY-RUN: Nenhuma alteração será salva no banco de dados')
        
        movimentacoes_criadas = 0
        movimentacoes_existentes = 0
        erros = 0
        
        with transaction.atomic():
            for escala_militar in escalas_militares:
                try:
                    # Verificar se já existe movimentação para esta escala
                    if BancoHoras.objects.filter(escala_militar=escala_militar).exists():
                        movimentacoes_existentes += 1
                        continue
                    
                    if not dry_run:
                        # Gerar movimentação
                        movimentacao = BancoHoras.gerar_movimentacao_escala(
                            escala_militar, 
                            tipo_movimentacao='ENTRADA'
                        )
                        
                        if movimentacao:
                            movimentacoes_criadas += 1
                            self.stdout.write(
                                f'✓ Criada movimentação para {escala_militar.militar.nome_guerra} '
                                f'em {escala_militar.escala.data} - {movimentacao.horas}h'
                            )
                        else:
                            self.stdout.write(
                                f'⚠ Não foi possível gerar movimentação para {escala_militar.militar.nome_guerra} '
                                f'em {escala_militar.escala.data} (horas inválidas)'
                            )
                    else:
                        # Simular criação
                        if escala_militar.hora_fim and escala_militar.hora_inicio:
                            from datetime import datetime, timedelta
                            inicio = datetime.combine(escala_militar.escala.data, escala_militar.hora_inicio)
                            fim = datetime.combine(escala_militar.escala.data, escala_militar.hora_fim)
                            
                            if fim <= inicio:
                                fim += timedelta(days=1)
                            
                            duracao = fim - inicio
                            horas = duracao.total_seconds() / 3600
                            
                            if horas > 0:
                                movimentacoes_criadas += 1
                                self.stdout.write(
                                    f'[DRY-RUN] ✓ Seria criada movimentação para {escala_militar.militar.nome_guerra} '
                                    f'em {escala_militar.escala.data} - {horas:.2f}h'
                                )
                
                except Exception as e:
                    erros += 1
                    self.stdout.write(
                        f'✗ Erro ao processar {escala_militar.militar.nome_guerra} '
                        f'em {escala_militar.escala.data}: {str(e)}'
                    )
        
        # Resumo
        self.stdout.write('\n' + '='*50)
        self.stdout.write('RESUMO DA EXECUÇÃO:')
        self.stdout.write(f'Total de escalas processadas: {total_escalas}')
        self.stdout.write(f'Movimentações criadas: {movimentacoes_criadas}')
        self.stdout.write(f'Movimentações já existentes: {movimentacoes_existentes}')
        self.stdout.write(f'Erros: {erros}')
        
        if dry_run:
            self.stdout.write('\nPara executar realmente, remova a opção --dry-run')
        else:
            self.stdout.write('\nBanco de horas atualizado com sucesso!')


