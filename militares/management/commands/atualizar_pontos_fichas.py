from django.core.management.base import BaseCommand
from militares.models import FichaConceitoOficiais, FichaConceitoPracas


class Command(BaseCommand):
    help = 'Atualiza os pontos de todas as fichas de conceito'

    def handle(self, *args, **options):
        self.stdout.write('Atualizando pontos das fichas de conceito...')
        
        # Atualizar fichas de oficiais
        fichas_oficiais = FichaConceitoOficiais.objects.all()
        for ficha in fichas_oficiais:
            pontos_antigos = ficha.pontos
            ficha.save()  # Isso vai recalcular os pontos
            pontos_novos = ficha.pontos
            self.stdout.write(
                f'Oficial {ficha.militar.nome_completo}: {pontos_antigos} -> {pontos_novos}'
            )
        
        # Atualizar fichas de praças
        fichas_pracas = FichaConceitoPracas.objects.all()
        for ficha in fichas_pracas:
            pontos_antigos = ficha.pontos
            ficha.save()  # Isso vai recalcular os pontos
            pontos_novos = ficha.pontos
            self.stdout.write(
                f'Praça {ficha.militar.nome_completo}: {pontos_antigos} -> {pontos_novos}'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Atualização concluída! {fichas_oficiais.count()} fichas de oficiais e {fichas_pracas.count()} fichas de praças atualizadas.'
            )
        ) 