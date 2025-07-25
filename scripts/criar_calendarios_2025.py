#!/usr/bin/env python
"""
Script para criar os calendários de promoções de 2025
baseado nos dados fornecidos pelo usuário.
"""

import os
import sys
import django
from datetime import datetime, date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CalendarioPromocao, ItemCalendarioPromocao

def criar_calendario_2025():
    """Cria os calendários de promoções para 2025"""
    
    # Dados do 1º semestre de 2025
    dados_1semestre = [
        ('FIXACAO_VAGAS', '2025-03-12', '2025-03-15', 1),
        ('ENCAMINHAMENTO_FICHAS', '2025-03-08', '2025-03-18', 2),
        ('INSPECAO_SAUDE', '2025-03-19', '2025-03-22', 3),
        ('PUBLICACAO_INSPECAO', '2025-03-12', '2025-03-27', 4),
        ('PRAZO_RECURSO_INSPECAO', '2025-04-01', '2025-04-03', 5),
        ('ANALISE_RECURSO_INSPECAO', '2025-04-04', '2025-04-05', 6),
        ('INSPECAO_RECURSOS', '2025-04-08', '2025-04-10', 7),
        ('PUBLICACAO_RECURSOS', '2025-04-08', '2025-04-12', 8),
        ('ANALISE_QUADRO', '2025-04-15', '2025-04-17', 9),
        ('PUBLICACAO_QUADRO', '2025-04-15', '2025-04-19', 10),
        ('PRAZO_RECURSO_QUADRO', '2025-04-22', '2025-05-03', 11),
        ('ANALISE_RECURSO_QUADRO', '2025-05-06', '2025-05-08', 12),
        ('ANALISE_ALTERACOES', '2025-05-09', '2025-05-10', 13),
        ('PUBLICACAO_ALTERACOES', '2025-05-09', '2025-05-15', 14),
        ('PROPOSTA_PROMOCAO', '2025-05-15', '2025-06-18', 15),
        ('DATA_PROMOCAO', '2025-07-18', '2025-07-18', 16),
    ]
    
    # Dados do 2º semestre de 2025
    dados_2semestre = [
        ('FIXACAO_VAGAS', '2025-08-01', '2025-08-03', 1),
        ('ENCAMINHAMENTO_FICHAS', '2025-08-04', '2025-08-14', 2),
        ('INSPECAO_SAUDE', '2025-08-12', '2025-08-16', 3),
        ('PUBLICACAO_INSPECAO', '2025-08-12', '2025-08-23', 4),
        ('PRAZO_RECURSO_INSPECAO', '2025-08-26', '2025-08-28', 5),
        ('ANALISE_RECURSO_INSPECAO', '2025-08-29', '2025-08-30', 6),
        ('INSPECAO_RECURSOS', '2025-08-23', '2025-08-27', 7),
        ('PUBLICACAO_RECURSOS', '2025-08-23', '2025-09-04', 8),
        ('ANALISE_QUADRO', '2025-09-05', '2025-09-09', 9),
        ('PUBLICACAO_QUADRO', '2025-09-05', '2025-09-11', 10),
        ('PRAZO_RECURSO_QUADRO', '2025-09-12', '2025-09-27', 11),
        ('ANALISE_RECURSO_QUADRO', '2025-09-30', '2025-10-02', 12),
        ('ANALISE_ALTERACOES', '2025-10-03', '2025-10-04', 13),
        ('PUBLICACAO_ALTERACOES', '2025-10-03', '2025-10-09', 14),
        ('PROPOSTA_PROMOCAO', '2025-10-09', '2025-11-25', 15),
        ('DATA_PROMOCAO', '2025-12-25', '2025-12-25', 16),
    ]
    
    # Criar calendário do 1º semestre
    calendario_1sem, created_1sem = CalendarioPromocao.objects.get_or_create(
        ano='2025',
        semestre='1',
        defaults={
            'ativo': True,
            'observacoes': 'Calendário de promoções do 1º semestre de 2025 - CBMEPI'
        }
    )
    
    if created_1sem:
        print(f"✓ Calendário 1º semestre 2025 criado com sucesso!")
    else:
        print(f"⚠ Calendário 1º semestre 2025 já existe. Atualizando itens...")
        # Limpar itens existentes
        calendario_1sem.itens.all().delete()
    
    # Adicionar itens do 1º semestre
    for tipo_atividade, data_inicio, data_fim, ordem in dados_1semestre:
        ItemCalendarioPromocao.objects.create(
            calendario=calendario_1sem,
            tipo_atividade=tipo_atividade,
            data_inicio=datetime.strptime(data_inicio, '%Y-%m-%d').date(),
            data_fim=datetime.strptime(data_fim, '%Y-%m-%d').date(),
            ordem=ordem
        )
    
    print(f"✓ {len(dados_1semestre)} itens adicionados ao 1º semestre")
    
    # Criar calendário do 2º semestre
    calendario_2sem, created_2sem = CalendarioPromocao.objects.get_or_create(
        ano='2025',
        semestre='2',
        defaults={
            'ativo': True,
            'observacoes': 'Calendário de promoções do 2º semestre de 2025 - CBMEPI'
        }
    )
    
    if created_2sem:
        print(f"✓ Calendário 2º semestre 2025 criado com sucesso!")
    else:
        print(f"⚠ Calendário 2º semestre 2025 já existe. Atualizando itens...")
        # Limpar itens existentes
        calendario_2sem.itens.all().delete()
    
    # Adicionar itens do 2º semestre
    for tipo_atividade, data_inicio, data_fim, ordem in dados_2semestre:
        ItemCalendarioPromocao.objects.create(
            calendario=calendario_2sem,
            tipo_atividade=tipo_atividade,
            data_inicio=datetime.strptime(data_inicio, '%Y-%m-%d').date(),
            data_fim=datetime.strptime(data_fim, '%Y-%m-%d').date(),
            ordem=ordem
        )
    
    print(f"✓ {len(dados_2semestre)} itens adicionados ao 2º semestre")
    
    # Resumo final
    print("\n" + "="*50)
    print("RESUMO DOS CALENDÁRIOS CRIADOS:")
    print("="*50)
    
    calendarios = CalendarioPromocao.objects.filter(ano='2025').order_by('semestre')
    for calendario in calendarios:
        print(f"\n📅 {calendario.periodo_completo}")
        print(f"   Status: {'✅ Ativo' if calendario.ativo else '❌ Inativo'}")
        print(f"   Itens: {calendario.itens.count()}")
        print(f"   Criado em: {calendario.data_criacao.strftime('%d/%m/%Y %H:%M')}")
        
        # Mostrar próximas atividades
        hoje = date.today()
        proximas = calendario.itens.filter(data_fim__gte=hoje).order_by('data_fim')[:3]
        if proximas:
            print("   Próximas atividades:")
            for item in proximas:
                status = "🟡 Em andamento" if item.data_inicio <= hoje <= item.data_fim else "⏳ Pendente"
                print(f"     • {item.get_tipo_atividade_display()} ({item.periodo_formatado}) - {status}")
    
    print("\n" + "="*50)
    print("✅ Processo concluído com sucesso!")
    print("="*50)

if __name__ == '__main__':
    print("🚀 Iniciando criação dos calendários de promoções 2025...")
    print("="*50)
    
    try:
        criar_calendario_2025()
    except Exception as e:
        print(f"❌ Erro durante a criação: {str(e)}")
        sys.exit(1) 