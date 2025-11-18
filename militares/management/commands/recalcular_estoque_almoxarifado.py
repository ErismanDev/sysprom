from django.core.management.base import BaseCommand
from militares.models import ProdutoAlmoxarifado


class Command(BaseCommand):
    help = 'Recalcula o estoque de todos os itens do almoxarifado baseado em entradas e saídas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--item-id',
            type=int,
            help='ID do item específico para recalcular (opcional)',
        )
        parser.add_argument(
            '--diagnostico',
            action='store_true',
            help='Mostra diagnóstico detalhado do cálculo',
        )

    def handle(self, *args, **options):
        item_id = options.get('item_id')
        diagnostico = options.get('diagnostico')
        
        if item_id:
            try:
                item = ProdutoAlmoxarifado.objects.get(pk=item_id)
                self.recalcular_item(item, diagnostico)
            except ProdutoAlmoxarifado.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Item com ID {item_id} não encontrado.'))
        else:
            # Recalcular todos os itens
            itens = ProdutoAlmoxarifado.objects.all()
            total = itens.count()
            self.stdout.write(f'Recalculando estoque de {total} itens...\n')
            
            corrigidos = 0
            for item in itens:
                if self.recalcular_item(item, False):
                    corrigidos += 1
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Concluído! {corrigidos} itens foram corrigidos de {total} total.'))

    def recalcular_item(self, item, mostrar_diagnostico=False):
        """Recalcula o estoque de um item"""
        quantidade_antes = item.quantidade_atual
        
        # Recalcular
        item.recalcular_quantidade_atual()
        
        quantidade_depois = item.quantidade_atual
        
        if mostrar_diagnostico or quantidade_antes != quantidade_depois:
            diagnostico = item.diagnosticar_estoque()
            
            self.stdout.write(f'\n📦 Item: {item.codigo} - {item.descricao}')
            self.stdout.write(f'   Quantidade antes: {quantidade_antes}')
            self.stdout.write(f'   Quantidade depois: {quantidade_depois}')
            self.stdout.write(f'   Total entradas: {diagnostico["total_entradas"]}')
            self.stdout.write(f'   Total saídas: {diagnostico["total_saidas"]}')
            self.stdout.write(f'   Calculado: {diagnostico["calculado"]}')
            
            if diagnostico["diferenca"] != 0:
                self.stdout.write(self.style.WARNING(f'   ⚠️ Diferença: {diagnostico["diferenca"]}'))
            
            if mostrar_diagnostico:
                self.stdout.write(f'\n   Entradas ({len(diagnostico["entradas_detalhes"])}):')
                for e in diagnostico["entradas_detalhes"]:
                    obs = f" ({e['observacoes']})" if e['observacoes'] else ""
                    self.stdout.write(f'      - ID {e["id"]}: {e["quantidade"]} ({e["tipo"]}) - {e["data"]}{obs}')
                
                self.stdout.write(f'\n   Saídas ({len(diagnostico["saidas_detalhes"])}):')
                for s in diagnostico["saidas_detalhes"]:
                    self.stdout.write(f'      - ID {s["id"]}: {s["quantidade"]} ({s["tipo"]}) - {s["data"]}')
        
        return quantidade_antes != quantidade_depois

