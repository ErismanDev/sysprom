#!/usr/bin/env python
"""
Script para ativar todos os cadastros que possuem campo 'ativo'
"""
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.db import transaction
from militares.models import (
    CargoComissao, Intersticio, QuadroAcesso, Curso, 
    MedalhaCondecoracao, PrevisaoVaga, MembroComissao, ModeloAta
)

def ativar_todos_cadastros():
    """
    Ativa todos os cadastros que possuem campo 'ativo'
    """
    print("=== ATIVANDO TODOS OS CADASTROS ===")
    print()
    
    # Lista de modelos para ativar
    modelos_para_ativar = [
        ('Cargos da Comissão', CargoComissao),
        ('Interstícios', Intersticio),
        ('Quadros de Acesso', QuadroAcesso),
        ('Cursos', Curso),
        ('Medalhas e Condecorações', MedalhaCondecoracao),
        ('Previsões de Vagas', PrevisaoVaga),
        ('Membros da Comissão', MembroComissao),
        ('Modelos de Ata', ModeloAta),
    ]
    
    total_geral = 0
    
    with transaction.atomic():
        for nome, modelo in modelos_para_ativar:
            try:
                # Contar registros inativos
                registros_inativos = modelo.objects.filter(ativo=False).count()
                
                if registros_inativos > 0:
                    # Ativar todos os registros
                    modelo.objects.filter(ativo=False).update(ativo=True)
                    print(f"✓ {nome}: {registros_inativos} registros ativados")
                    total_geral += registros_inativos
                else:
                    print(f"✓ {nome}: Nenhum registro inativo encontrado")
                    
            except Exception as e:
                print(f"✗ {nome}: Erro - {str(e)}")
    
    print()
    print(f"=== RESUMO ===")
    print(f"Total de registros ativados: {total_geral}")
    print("Todos os cadastros foram ativados com sucesso!")

if __name__ == '__main__':
    ativar_todos_cadastros() 