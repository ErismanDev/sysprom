from django.core.management.base import BaseCommand
from django.utils import timezone
from militares.models import Publicacao


class Command(BaseCommand):
    help = 'Verifica as notas que aparecem na lista'

    def handle(self, *args, **options):
        ano_atual = timezone.localtime(timezone.now()).year
        
        # Buscar todas as notas como na view
        publicacoes = Publicacao.objects.filter(
            tipo='NOTA',
            ativo=True
        ).order_by('-data_criacao', '-id')
        
        self.stdout.write(f'Total de notas na lista: {publicacoes.count()}')
        self.stdout.write('')
        self.stdout.write('PRIMEIRAS 20 NOTAS:')
        self.stdout.write('-' * 60)
        
        for i, nota in enumerate(publicacoes[:20]):
            self.stdout.write(f'{i+1:2d}. ID: {nota.id:3d} | Número: "{nota.numero:15s}" | Título: {nota.titulo[:30]}...')
        
        if publicacoes.count() > 20:
            self.stdout.write(f'... e mais {publicacoes.count() - 20} notas')
        
        self.stdout.write('')
        self.stdout.write('ANÁLISE DE NÚMEROS:')
        self.stdout.write('-' * 60)
        
        # Contar formatos diferentes
        formatos = {}
        for nota in publicacoes:
            formato = nota.numero
            if formato in formatos:
                formatos[formato] += 1
            else:
                formatos[formato] = 1
        
        for formato, count in sorted(formatos.items()):
            self.stdout.write(f'"{formato}": {count} notas')
        
        self.stdout.write('')
        self.stdout.write('NOTAS COM PROBLEMAS:')
        self.stdout.write('-' * 60)
        
        problemas = 0
        for nota in publicacoes:
            numero = nota.numero
            tem_problema = False
            motivo = []
            
            # Verificar se tem ano duplicado
            if f"/{ano_atual}/{ano_atual}" in numero:
                tem_problema = True
                motivo.append("ano duplicado")
            
            # Verificar se não tem ano
            if not f"/{ano_atual}" in numero and not numero.isdigit():
                tem_problema = True
                motivo.append("sem ano")
            
            # Verificar se tem formato estranho
            if numero.count('/') > 1:
                tem_problema = True
                motivo.append("múltiplas barras")
            
            if tem_problema:
                problemas += 1
                self.stdout.write(f'ID: {nota.id:3d} | "{numero}" | Problemas: {", ".join(motivo)}')
        
        if problemas == 0:
            self.stdout.write('Nenhuma nota com problemas encontrada!')
        else:
            self.stdout.write(f'Total de notas com problemas: {problemas}')
