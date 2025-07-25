from django.core.management.base import BaseCommand
from militares.models import Militar


class Command(BaseCommand):
    help = 'Corrige a numeração de antiguidade de todos os postos, removendo gaps e duplicatas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--posto',
            type=str,
            help='Corrigir apenas um posto específico (ex: CB, TC, MJ, etc.)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar o que seria corrigido sem fazer alterações'
        )

    def handle(self, *args, **options):
        posto_especifico = options.get('posto')
        dry_run = options.get('dry_run')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY-RUN - Nenhuma alteração será feita\n'))
        
        # Lista de postos para verificar (excluindo NVRR)
        postos = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        
        if posto_especifico:
            if posto_especifico not in postos:
                self.stdout.write(
                    self.style.ERROR(f'❌ Posto "{posto_especifico}" não é válido. Postos válidos: {", ".join(postos)}')
                )
                return
            postos = [posto_especifico]
        
        total_corrigidos = 0
        
        for posto in postos:
            self.stdout.write(f'\n=== CORRIGINDO POSTO: {posto} ===')
            
            # Buscar militares do posto (excluindo NVRR)
            militares = Militar.objects.filter(
                posto_graduacao=posto,
                situacao='AT'
            ).exclude(
                quadro='NVRR'
            ).exclude(
                posto_graduacao='NVRR'
            ).order_by('numeracao_antiguidade')
            
            if not militares.exists():
                self.stdout.write(f'  ℹ️  Nenhum militar encontrado para o posto {posto}')
                continue
            
            self.stdout.write(f'  📊 Total de militares: {militares.count()}')
            
            # Verificar problemas
            problemas = []
            numeracoes = [m.numeracao_antiguidade for m in militares if m.numeracao_antiguidade is not None]
            numeracoes.sort()
            
            if numeracoes:
                # Verificar se começa em 1
                if numeracoes[0] != 1:
                    problemas.append(f"Numeração não começa em 1 (começa em {numeracoes[0]})")
                
                # Verificar gaps
                for i in range(len(numeracoes) - 1):
                    if numeracoes[i+1] - numeracoes[i] > 1:
                        problemas.append(f"Gap entre {numeracoes[i]} e {numeracoes[i+1]}")
                
                # Verificar duplicatas
                if len(numeracoes) != len(set(numeracoes)):
                    problemas.append("Numerações duplicadas")
                
                # Verificar se há militares sem numeração
                militares_sem_num = militares.filter(numeracao_antiguidade__isnull=True).count()
                if militares_sem_num > 0:
                    problemas.append(f"{militares_sem_num} militares sem numeração")
            
            if problemas:
                self.stdout.write(f'  ❌ Problemas encontrados:')
                for problema in problemas:
                    self.stdout.write(f'    - {problema}')
                
                if not dry_run:
                    self.stdout.write(f'  🔧 Corrigindo...')
                    # Reordenar automaticamente
                    for i, militar in enumerate(militares, 1):
                        if militar.numeracao_antiguidade != i:
                            self.stdout.write(f'    {militar.nome_completo}: {militar.numeracao_antiguidade}º -> {i}º')
                            militar.numeracao_antiguidade = i
                            militar.save(update_fields=['numeracao_antiguidade'])
                            total_corrigidos += 1
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Posto {posto} corrigido!'))
                else:
                    self.stdout.write(f'  🔧 Seria corrigido:')
                    for i, militar in enumerate(militares, 1):
                        if militar.numeracao_antiguidade != i:
                            self.stdout.write(f'    {militar.nome_completo}: {militar.numeracao_antiguidade}º -> {i}º')
                            total_corrigidos += 1
            else:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Posto {posto} está correto'))
        
        # Resumo final
        self.stdout.write(f'\n=== RESUMO ===')
        if dry_run:
            self.stdout.write(f'🔍 Modo DRY-RUN: {total_corrigidos} correções seriam feitas')
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ {total_corrigidos} correções realizadas com sucesso!'))
        
        self.stdout.write(f'\n💡 Dica: Use --dry-run para ver o que seria corrigido antes de executar') 