"""
Script para popular categorias e subcategorias do almoxarifado
Execute: python manage.py popular_categorias_almoxarifado
"""

from django.core.management.base import BaseCommand
from militares.models import Categoria, Subcategoria


class Command(BaseCommand):
    help = 'Popula as categorias e subcategorias do almoxarifado'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população de categorias e subcategorias...')
        
        # Dados das categorias e subcategorias
        categorias_data = [
            {
                'nome': 'Equipamentos Operacionais',
                'descricao': 'Equipamentos utilizados em operações de combate a incêndio, salvamento e resgate',
                'subcategorias': [
                    'Equipamentos de combate a incêndio',
                    'Equipamentos de salvamento terrestre',
                    'Equipamentos de salvamento aquático',
                    'Equipamentos de salvamento em altura',
                    'Equipamentos de salvamento veicular',
                    'Equipamentos de busca e resgate em estruturas colapsadas (BREC)',
                    'Equipamentos de combate a incêndios florestais',
                    'Equipamentos de iluminação e sinalização de emergência',
                    'Equipamentos de comunicação operacional (rádios, repetidoras, antenas)',
                    'Equipamentos de proteção respiratória (SCBA, filtros, máscaras)',
                ]
            },
            {
                'nome': 'Equipamentos de Proteção Individual (EPI)',
                'descricao': 'Equipamentos de proteção individual para uso operacional',
                'subcategorias': [
                    'Capacetes',
                    'Luvas',
                    'Botas',
                    'Capas e calças de aproximação',
                    'Conjuntos de combate a incêndio urbano/florestal',
                    'Cintos de ancoragem e talabartes',
                    'Óculos de proteção e viseiras',
                    'Protetores auditivos',
                    'Máscaras faciais',
                ]
            },
            {
                'nome': 'Equipamentos e Materiais para Viaturas',
                'descricao': 'Equipamentos e materiais específicos para viaturas operacionais',
                'subcategorias': [
                    'Itens de sinalização sonora e luminosa',
                    'Ferramentas e acessórios veiculares',
                    'Equipamentos de resgate embarcados',
                    'Kits de primeiros socorros veiculares',
                    'Mangueiras, esguichos e conexões',
                    'Suportes e fixadores de equipamentos',
                    'Materiais de limpeza e conservação de viaturas',
                    'Tanques, bombas e válvulas',
                ]
            },
            {
                'nome': 'Equipamentos de Engenharia e Logística',
                'descricao': 'Equipamentos de engenharia e logística para operações e manutenção',
                'subcategorias': [
                    'Ferramentas manuais e elétricas',
                    'Máquinas e equipamentos de oficina',
                    'Materiais de construção e manutenção predial',
                    'Geradores e transformadores portáteis',
                    'Bombas hidráulicas e motobombas',
                    'Compressores de ar',
                    'Equipamentos de medição e topografia',
                    'Estruturas metálicas e lonas para abrigos temporários',
                ]
            },
            {
                'nome': 'Materiais e Equipamentos de Saúde',
                'descricao': 'Materiais e equipamentos para atendimento pré-hospitalar e emergências médicas',
                'subcategorias': [
                    'Kits de primeiros socorros',
                    'Macas, pranchas e colares cervicais',
                    'Desfibriladores (DEA)',
                    'Equipamentos de oxigenoterapia',
                    'Materiais de imobilização e transporte de vítimas',
                    'Materiais hospitalares de consumo (luvas, gazes, ataduras, etc.)',
                    'Medicamentos de uso emergencial',
                    'Equipamentos para suporte básico e avançado de vida',
                ]
            },
            {
                'nome': 'Materiais de Manutenção e Almoxarifado',
                'descricao': 'Materiais diversos para manutenção e funcionamento do almoxarifado',
                'subcategorias': [
                    'Ferramentas diversas',
                    'Materiais elétricos e hidráulicos',
                    'Materiais de pintura',
                    'Materiais de limpeza e higienização',
                    'Equipamentos e utensílios de cozinha',
                    'Equipamentos e materiais de escritório',
                    'Materiais de expediente (papel, caneta, toner, etc.)',
                    'Equipamentos de informática e periféricos',
                ]
            },
            {
                'nome': 'Materiais Didáticos e de Treinamento',
                'descricao': 'Materiais e equipamentos para treinamento e instrução',
                'subcategorias': [
                    'Equipamentos de simulação e instrução (manequins, simuladores, extintores de treinamento)',
                    'Projetores, telas e equipamentos audiovisuais',
                    'Materiais pedagógicos e impressos',
                    'Fardamento escolar e uniformes de instrução',
                    'Materiais esportivos e de recreação',
                    'Equipamentos de ginástica e treinamento físico',
                ]
            },
            {
                'nome': 'Materiais de Infraestrutura e Construção',
                'descricao': 'Materiais para construção e manutenção de infraestrutura',
                'subcategorias': [
                    'Cimento, areia, brita e materiais básicos',
                    'Ferragens, telhas, tijolos, blocos e pisos',
                    'Tintas e vernizes',
                    'Equipamentos sanitários e hidráulicos',
                    'Iluminação e fiação elétrica',
                    'Portas, janelas e acessórios de construção',
                ]
            },
            {
                'nome': 'Materiais e Equipamentos de Informática',
                'descricao': 'Equipamentos e materiais de tecnologia da informação',
                'subcategorias': [
                    'Computadores e notebooks',
                    'Impressoras e scanners',
                    'Roteadores e switches',
                    'Câmeras de segurança e vigilância',
                    'Softwares de gestão e operação',
                    'Equipamentos para rede e infraestrutura de TI',
                    'Periféricos e suprimentos de informática',
                ]
            },
            {
                'nome': 'Materiais Administrativos e de Escritório',
                'descricao': 'Materiais e equipamentos para uso administrativo',
                'subcategorias': [
                    'Mobiliário (mesas, cadeiras, armários, arquivos)',
                    'Materiais de expediente',
                    'Equipamentos de protocolo e arquivo',
                    'Uniformes administrativos',
                    'Materiais de sinalização interna e externa',
                ]
            },
            {
                'nome': 'Materiais para Defesa Civil e Ações Humanitárias',
                'descricao': 'Materiais e equipamentos para ações de defesa civil e humanitárias',
                'subcategorias': [
                    'Kits de abrigo e acolhimento (colchonetes, cobertores, lonas)',
                    'Cestas básicas e kits de higiene',
                    'Equipamentos de resgate em enchentes e desastres',
                    'Barracas, tendas e módulos habitacionais',
                    'Equipamentos de comunicação emergencial',
                ]
            },
            {
                'nome': 'Materiais Permanentes e de Patrimônio',
                'descricao': 'Materiais permanentes e de patrimônio da instituição',
                'subcategorias': [
                    'Móveis e utensílios duráveis',
                    'Equipamentos eletrônicos',
                    'Máquinas e ferramentas',
                    'Veículos e embarcações',
                    'Equipamentos de academia',
                    'Geradores e sistemas de energia',
                ]
            },
        ]
        
        categorias_criadas = 0
        subcategorias_criadas = 0
        
        for cat_data in categorias_data:
            # Criar ou obter categoria
            categoria, created = Categoria.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={
                    'descricao': cat_data['descricao'],
                    'ativo': True
                }
            )
            
            if created:
                categorias_criadas += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Categoria criada: {categoria.nome}'))
            else:
                self.stdout.write(f'→ Categoria já existe: {categoria.nome}')
            
            # Criar subcategorias
            for subcat_nome in cat_data['subcategorias']:
                subcategoria, created = Subcategoria.objects.get_or_create(
                    categoria=categoria,
                    nome=subcat_nome,
                    defaults={
                        'ativo': True
                    }
                )
                
                if created:
                    subcategorias_criadas += 1
                    self.stdout.write(f'  ✓ Subcategoria criada: {subcategoria.nome}')
                else:
                    self.stdout.write(f'  → Subcategoria já existe: {subcategoria.nome}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'✓ Processo concluído! '
            f'{categorias_criadas} categorias e {subcategorias_criadas} subcategorias criadas.'
        ))

