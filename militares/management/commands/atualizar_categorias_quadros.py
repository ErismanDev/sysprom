from django.core.management.base import BaseCommand
from militares.models import QuadroAcesso


class Command(BaseCommand):
    help = 'Atualiza as categorias dos quadros de acesso existentes baseado nos militares'

    def handle(self, *args, **options):
        quadros = QuadroAcesso.objects.all()
        atualizados = 0
        
        for quadro in quadros:
            # Verificar se o quadro tem militares
            itens = quadro.itemquadroacesso_set.all()
            
            if itens.exists():
                # Verificar se são oficiais ou praças
                oficiais = itens.filter(
                    militar__posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
                ).exists()
                
                praças = itens.filter(
                    militar__posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
                ).exists()
                
                # Determinar categoria
                if praças and not oficiais:
                    nova_categoria = 'PRACAS'
                elif oficiais and not praças:
                    nova_categoria = 'OFICIAIS'
                else:
                    # Se tem ambos ou nenhum, manter o padrão
                    nova_categoria = quadro.categoria or 'OFICIAIS'
                
                # Atualizar se necessário
                if quadro.categoria != nova_categoria:
                    quadro.categoria = nova_categoria
                    quadro.save()
                    atualizados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Quadro {quadro.pk} atualizado: {quadro.categoria} -> {nova_categoria}'
                        )
                    )
            else:
                # Se não tem militares, manter como está
                if not quadro.categoria:
                    quadro.categoria = 'OFICIAIS'
                    quadro.save()
                    atualizados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Quadro {quadro.pk} sem militares: definido como OFICIAIS'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Processo concluído. {atualizados} quadros atualizados.')
        ) 