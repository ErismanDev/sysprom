#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso
from datetime import date

def limpar_quadros_duplicados():
    print("=== LIMPANDO QUADROS DUPLICADOS ===\n")
    
    # 1. Listar todos os quadros existentes
    print("1. QUADROS EXISTENTES:")
    print("-" * 50)
    
    quadros = QuadroAcesso.objects.all().order_by('tipo', 'data_promocao')
    print(f"Total de quadros: {quadros.count()}")
    
    for quadro in quadros:
        print(f"  ID: {quadro.id}, Tipo: {quadro.tipo}, Data: {quadro.data_promocao}, Status: {quadro.status}")
    
    # 2. Identificar quadros duplicados
    print(f"\n2. VERIFICANDO DUPLICATAS:")
    print("-" * 50)
    
    # Agrupar por tipo e data
    grupos = {}
    for quadro in quadros:
        chave = (quadro.tipo, quadro.data_promocao)
        if chave not in grupos:
            grupos[chave] = []
        grupos[chave].append(quadro)
    
    duplicatas = []
    for chave, lista_quadros in grupos.items():
        if len(lista_quadros) > 1:
            duplicatas.append((chave, lista_quadros))
            print(f"  Duplicata encontrada: {chave[0]} - {chave[1]}")
            for q in lista_quadros:
                print(f"    ID: {q.id}, Status: {q.status}")
    
    # 3. Limpar quadros duplicados (manter apenas o mais recente)
    print(f"\n3. LIMPANDO DUPLICATAS:")
    print("-" * 50)
    
    for chave, lista_quadros in duplicatas:
        # Ordenar por data de criação (mais recente primeiro)
        lista_ordenada = sorted(lista_quadros, key=lambda x: x.data_criacao, reverse=True)
        
        # Manter apenas o primeiro (mais recente)
        manter = lista_ordenada[0]
        excluir = lista_ordenada[1:]
        
        print(f"  Mantendo: ID {manter.id} (criado em {manter.data_criacao})")
        
        for quadro in excluir:
            print(f"  Excluindo: ID {quadro.id} (criado em {quadro.data_criacao})")
            quadro.delete()
    
    # 4. Verificar quadros vazios (sem itens)
    print(f"\n4. VERIFICANDO QUADROS VAZIOS:")
    print("-" * 50)
    
    quadros_vazios = []
    for quadro in QuadroAcesso.objects.all():
        if quadro.itemquadroacesso_set.count() == 0:
            quadros_vazios.append(quadro)
            print(f"  Quadro vazio: ID {quadro.id}, Tipo: {quadro.tipo}, Data: {quadro.data_promocao}")
    
    # 5. Perguntar se deve limpar quadros vazios
    if quadros_vazios:
        print(f"\n5. QUADROS VAZIOS ENCONTRADOS:")
        print("-" * 50)
        print(f"Total de quadros vazios: {len(quadros_vazios)}")
        
        # Por segurança, não excluir automaticamente
        print("  Quadros vazios não serão excluídos automaticamente por segurança.")
        print("  Você pode excluí-los manualmente se necessário.")
    
    # 6. Resumo final
    print(f"\n6. RESUMO FINAL:")
    print("-" * 50)
    
    quadros_finais = QuadroAcesso.objects.all()
    print(f"Total de quadros após limpeza: {quadros_finais.count()}")
    
    for quadro in quadros_finais:
        itens = quadro.itemquadroacesso_set.count()
        print(f"  ID: {quadro.id}, Tipo: {quadro.tipo}, Data: {quadro.data_promocao}, Itens: {itens}")
    
    print(f"\n✅ Limpeza concluída! Agora você pode criar novos quadros.")

if __name__ == "__main__":
    limpar_quadros_duplicados() 