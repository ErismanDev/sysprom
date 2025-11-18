from django.core.management.base import BaseCommand
from django.db import transaction
from militares.models import Publicacao, Orgao, GrandeComando, Unidade, SubUnidade


class Command(BaseCommand):
    help = 'Atualiza as origens das publicações para usar o formato hierárquico completo do organograma'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações no banco de dados',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita no banco de dados'))
        
        # Buscar todas as publicações ativas (todos os tipos)
        publicacoes = Publicacao.objects.filter(ativo=True, origem_publicacao__isnull=False)
        total_publicacoes = publicacoes.count()
        
        self.stdout.write(f'Encontradas {total_publicacoes} publicações para atualizar')
        
        if total_publicacoes == 0:
            self.stdout.write(self.style.WARNING('Nenhuma publicação encontrada'))
            return
        
        # Criar mapeamento de nomes para IDs do organograma
        mapeamento_organograma = self._criar_mapeamento_organograma()
        
        atualizadas = 0
        nao_encontradas = 0
        
        with transaction.atomic():
            for publicacao in publicacoes:
                origem_original = publicacao.origem_publicacao
                if not origem_original:
                    continue
                
                # Limpar a origem original (remover espaços extras e indentação)
                origem_limpa = origem_original.strip()
                
                # Tentar encontrar correspondência no organograma
                nova_origem = self._encontrar_origem_hierarquica(origem_limpa, mapeamento_organograma)
                
                if nova_origem:
                    if not dry_run:
                        publicacao.origem_publicacao = nova_origem
                        publicacao.save(update_fields=['origem_publicacao'])
                    
                    self.stdout.write(f'✓ {origem_original} → {nova_origem}')
                    atualizadas += 1
                else:
                    self.stdout.write(self.style.WARNING(f'✗ Não encontrada: {origem_original}'))
                    nao_encontradas += 1
        
        # Resumo
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total de publicações processadas: {total_publicacoes}')
        self.stdout.write(f'Atualizadas: {atualizadas}')
        self.stdout.write(f'Não encontradas: {nao_encontradas}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY-RUN: Nenhuma alteração foi feita'))
        else:
            self.stdout.write(self.style.SUCCESS('Atualização concluída com sucesso!'))

    def _criar_mapeamento_organograma(self):
        """Cria um mapeamento de nomes para a hierarquia completa do organograma"""
        mapeamento = {}
        
        # Buscar todos os órgãos
        orgaos = Orgao.objects.filter(ativo=True)
        for orgao in orgaos:
            # Adicionar órgão
            mapeamento[orgao.nome.lower()] = {
                'tipo': 'orgao',
                'hierarquia': orgao.nome,
                'orgao': orgao
            }
            
            # Adicionar grandes comandos
            for gc in orgao.grandes_comandos.filter(ativo=True):
                hierarquia_gc = f"{orgao.nome} | {gc.nome}"
                mapeamento[gc.nome.lower()] = {
                    'tipo': 'grande_comando',
                    'hierarquia': hierarquia_gc,
                    'orgao': orgao,
                    'grande_comando': gc
                }
                
                # Adicionar unidades
                for unidade in gc.unidades.filter(ativo=True):
                    hierarquia_unidade = f"{orgao.nome} | {gc.nome} | {unidade.nome}"
                    mapeamento[unidade.nome.lower()] = {
                        'tipo': 'unidade',
                        'hierarquia': hierarquia_unidade,
                        'orgao': orgao,
                        'grande_comando': gc,
                        'unidade': unidade
                    }
                    
                    # Adicionar sub-unidades
                    for sub_unidade in unidade.sub_unidades.filter(ativo=True):
                        hierarquia_sub = f"{orgao.nome} | {gc.nome} | {unidade.nome} | {sub_unidade.nome}"
                        mapeamento[sub_unidade.nome.lower()] = {
                            'tipo': 'sub_unidade',
                            'hierarquia': hierarquia_sub,
                            'orgao': orgao,
                            'grande_comando': gc,
                            'unidade': unidade,
                            'sub_unidade': sub_unidade
                        }
        
        return mapeamento

    def _encontrar_origem_hierarquica(self, origem_limpa, mapeamento):
        """Encontra a origem hierárquica correspondente"""
        origem_lower = origem_limpa.lower()
        
        # Tentar busca exata primeiro
        if origem_lower in mapeamento:
            return mapeamento[origem_lower]['hierarquia']
        
        # Tentar busca parcial (contém)
        for nome, dados in mapeamento.items():
            if nome in origem_lower or origem_lower in nome:
                return dados['hierarquia']
        
        # Tentar busca por palavras-chave comuns
        palavras_chave = {
            'comando geral': 'Comando Geral',
            'ajudância geral': 'Comando Geral | Ajudância Geral',
            'dgp': 'Comando Geral | Diretoria de Gestão de Pessoal',
            'grupamento': 'Comando Geral | Grande Comando | Grupamento',
            'subgrupamento': 'Comando Geral | Grande Comando | Grupamento | Subgrupamento',
            '1º gbm': 'Comando Geral | 1º Grande Comando | 1º Grupamento de Bombeiros Militar',
            '1º sgbm': 'Comando Geral | 1º Grande Comando | 1º Grupamento de Bombeiros Militar | 1º Subgrupamento do 1º Grupamento de Bombeiros Militar',
            'sistema': 'Sistema',
            'comissão de promoções': 'Comando Geral | Comissão de Promoções',
            'comissao de promocoes': 'Comando Geral | Comissão de Promoções',
            'comisso de promoes': 'Comando Geral | Comissão de Promoções',
        }
        
        for palavra, hierarquia in palavras_chave.items():
            if palavra in origem_lower:
                return hierarquia
        
        return None
