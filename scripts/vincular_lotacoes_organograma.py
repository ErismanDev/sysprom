#!/usr/bin/env python
"""
Script para vincular automaticamente lotações às estruturas organizacionais
baseado na correspondência de nomes.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Lotacao, Orgao, GrandeComando, Unidade, SubUnidade


def vincular_lotacoes_organograma():
    """
    Vincula lotações às estruturas organizacionais baseado na correspondência de nomes
    """
    print("Iniciando vinculação de lotações ao organograma...")
    
    # Buscar lotações sem vinculação
    lotacoes_sem_vinculacao = Lotacao.objects.filter(
        orgao__isnull=True,
        grande_comando__isnull=True,
        unidade__isnull=True,
        sub_unidade__isnull=True
    )
    
    print(f"Encontradas {lotacoes_sem_vinculacao.count()} lotações sem vinculação")
    
    vinculacoes_realizadas = 0
    
    for lotacao in lotacoes_sem_vinculacao:
        print(f"\nProcessando: {lotacao.lotacao}")
        
        # Tentar vincular por nome exato
        vinculada = False
        
        # 1. Tentar vincular a Sub-unidade
        sub_unidade = SubUnidade.objects.filter(
            nome__iexact=lotacao.lotacao,
            ativo=True
        ).first()
        
        if sub_unidade:
            lotacao.sub_unidade = sub_unidade
            lotacao.unidade = sub_unidade.unidade
            lotacao.grande_comando = sub_unidade.unidade.grande_comando
            lotacao.orgao = sub_unidade.unidade.grande_comando.orgao
            lotacao.save()
            print(f"  ✓ Vinculada à Sub-unidade: {sub_unidade.nome}")
            vinculada = True
        
        # 2. Tentar vincular a Unidade
        elif not vinculada:
            unidade = Unidade.objects.filter(
                nome__iexact=lotacao.lotacao,
                ativo=True
            ).first()
            
            if unidade:
                lotacao.unidade = unidade
                lotacao.grande_comando = unidade.grande_comando
                lotacao.orgao = unidade.grande_comando.orgao
                lotacao.save()
                print(f"  ✓ Vinculada à Unidade: {unidade.nome}")
                vinculada = True
        
        # 3. Tentar vincular a Grande Comando
        elif not vinculada:
            grande_comando = GrandeComando.objects.filter(
                nome__iexact=lotacao.lotacao,
                ativo=True
            ).first()
            
            if grande_comando:
                lotacao.grande_comando = grande_comando
                lotacao.orgao = grande_comando.orgao
                lotacao.save()
                print(f"  ✓ Vinculada ao Grande Comando: {grande_comando.nome}")
                vinculada = True
        
        # 4. Tentar vincular a Órgão
        elif not vinculada:
            orgao = Orgao.objects.filter(
                nome__iexact=lotacao.lotacao,
                ativo=True
            ).first()
            
            if orgao:
                lotacao.orgao = orgao
                lotacao.save()
                print(f"  ✓ Vinculada ao Órgão: {orgao.nome}")
                vinculada = True
        
        # 5. Tentar vinculação por correspondência parcial
        if not vinculada:
            # Buscar por correspondência parcial em Sub-unidades
            sub_unidades_parciais = SubUnidade.objects.filter(
                nome__icontains=lotacao.lotacao,
                ativo=True
            )
            
            if sub_unidades_parciais.exists():
                sub_unidade = sub_unidades_parciais.first()
                lotacao.sub_unidade = sub_unidade
                lotacao.unidade = sub_unidade.unidade
                lotacao.grande_comando = sub_unidade.unidade.grande_comando
                lotacao.orgao = sub_unidade.unidade.grande_comando.orgao
                lotacao.save()
                print(f"  ✓ Vinculada à Sub-unidade (parcial): {sub_unidade.nome}")
                vinculada = True
            
            # Buscar por correspondência parcial em Unidades
            elif not vinculada:
                unidades_parciais = Unidade.objects.filter(
                    nome__icontains=lotacao.lotacao,
                    ativo=True
                )
                
                if unidades_parciais.exists():
                    unidade = unidades_parciais.first()
                    lotacao.unidade = unidade
                    lotacao.grande_comando = unidade.grande_comando
                    lotacao.orgao = unidade.grande_comando.orgao
                    lotacao.save()
                    print(f"  ✓ Vinculada à Unidade (parcial): {unidade.nome}")
                    vinculada = True
        
        if vinculada:
            vinculacoes_realizadas += 1
        else:
            print(f"  ✗ Nenhuma correspondência encontrada para: {lotacao.lotacao}")
    
    print(f"\nVinculação concluída!")
    print(f"Total de vinculações realizadas: {vinculacoes_realizadas}")
    
    # Verificar resultado final
    lotacoes_sem_vinculacao_final = Lotacao.objects.filter(
        orgao__isnull=True,
        grande_comando__isnull=True,
        unidade__isnull=True,
        sub_unidade__isnull=True
    ).count()
    
    print(f"Lotações ainda sem vinculação: {lotacoes_sem_vinculacao_final}")


if __name__ == "__main__":
    vincular_lotacoes_organograma()
