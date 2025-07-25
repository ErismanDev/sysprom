#!/usr/bin/env python
"""
Script para verificar o status atual de todos os cadastros
"""
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.db import transaction
from militares.models import (
    Militar, CargoComissao, Intersticio, QuadroAcesso, Curso, 
    MedalhaCondecoracao, PrevisaoVaga, MembroComissao, ModeloAta,
    ComissaoPromocao
)

def verificar_status_cadastros():
    """
    Verifica o status atual de todos os cadastros
    """
    print("=== VERIFICANDO STATUS DOS CADASTROS ===")
    print()
    
    # Verificar militares por situação
    print("--- MILITARES POR SITUAÇÃO ---")
    from django.db.models import Count
    
    # Definir as escolhas de situação
    SITUACAO_CHOICES = [
        ('AT', 'Ativo'),
        ('IN', 'Inativo'),
        ('TR', 'Transferido'),
        ('AP', 'Aposentado'),
        ('EX', 'Exonerado'),
    ]
    
    situacoes = Militar.objects.values('situacao').annotate(total=Count('id')).order_by('situacao')
    
    for situacao in situacoes:
        situacao_display = dict(SITUACAO_CHOICES).get(situacao['situacao'], situacao['situacao'])
        print(f"  {situacao_display}: {situacao['total']} militares")
    
    print()
    
    # Verificar comissões por status
    print("--- COMISSÕES POR STATUS ---")
    status_comissoes = ComissaoPromocao.objects.values('status').annotate(total=Count('id')).order_by('status')
    
    for status in status_comissoes:
        status_display = dict(ComissaoPromocao.STATUS_CHOICES).get(status['status'], status['status'])
        print(f"  {status_display}: {status['total']} comissões")
    
    print()
    
    # Verificar registros ativos/inativos
    print("--- REGISTROS ATIVOS/INATIVOS ---")
    modelos_para_verificar = [
        ('Cargos da Comissão', CargoComissao),
        ('Interstícios', Intersticio),
        ('Quadros de Acesso', QuadroAcesso),
        ('Cursos', Curso),
        ('Medalhas e Condecorações', MedalhaCondecoracao),
        ('Previsões de Vagas', PrevisaoVaga),
        ('Membros da Comissão', MembroComissao),
        ('Modelos de Ata', ModeloAta),
    ]
    
    for nome, modelo in modelos_para_verificar:
        try:
            ativos = modelo.objects.filter(ativo=True).count()
            inativos = modelo.objects.filter(ativo=False).count()
            total = ativos + inativos
            
            print(f"  {nome}:")
            print(f"    Total: {total}")
            print(f"    Ativos: {ativos}")
            print(f"    Inativos: {inativos}")
            print()
            
        except Exception as e:
            print(f"  {nome}: Erro - {str(e)}")
            print()
    
    print("=== VERIFICAÇÃO CONCLUÍDA ===")

if __name__ == '__main__':
    verificar_status_cadastros() 