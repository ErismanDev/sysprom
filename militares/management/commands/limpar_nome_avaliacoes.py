from django.core.management.base import BaseCommand
from militares.models import AvaliacaoEnsino


class Command(BaseCommand):
    help = 'Remove o texto "ele se fez ouvir" do campo nome das avaliações'

    def handle(self, *args, **options):
        avaliacoes = AvaliacaoEnsino.objects.filter(nome__icontains='ele se fez ouvir')
        count = 0
        
        for avaliacao in avaliacoes:
            # Remover o texto indesejado
            if avaliacao.nome and "ele se fez ouvir" in avaliacao.nome.lower():
                # Gerar nome automaticamente baseado no tipo
                tipo_display = avaliacao.get_tipo_display()
                tipo_verificacao_display = avaliacao.get_tipo_verificacao_display() if avaliacao.tipo_verificacao else ''
                
                if avaliacao.tipo == 'RECUPERACAO':
                    avaliacao.nome = f"Recuperação - {avaliacao.disciplina.nome}"
                elif tipo_verificacao_display:
                    avaliacao.nome = f"{tipo_verificacao_display} - {tipo_display}"
                else:
                    avaliacao.nome = f"{tipo_display} - {avaliacao.disciplina.nome}"
                
                avaliacao.save()
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Avaliação ID {avaliacao.pk} corrigida: {avaliacao.nome}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal de avaliações corrigidas: {count}')
        )

