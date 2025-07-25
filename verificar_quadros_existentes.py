#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, Militar, FichaConceito

def verificar_quadros_existentes():
    print("=== VERIFICAÇÃO DE QUADROS DE ACESSO EXISTENTES ===\n")
    
    # Verificar todos os quadros de acesso
    quadros = QuadroAcesso.objects.all().order_by('-data_criacao')
    
    if not quadros.exists():
        print("❌ Nenhum quadro de acesso encontrado no sistema!")
        return
    
    print(f"📊 Total de quadros encontrados: {quadros.count()}\n")
    
    for i, quadro in enumerate(quadros, 1):
        print(f"--- QUADRO {i} ---")
        print(f"ID: {quadro.id}")
        print(f"Tipo: {quadro.get_tipo_display()}")
        print(f"Data de promoção: {quadro.data_promocao}")
        print(f"Data de criação: {quadro.data_criacao}")
        print(f"Status: {quadro.get_status_display()}")
        print(f"Ativo: {'Sim' if quadro.ativo else 'Não'}")
        
        # Verificar itens do quadro
        itens = quadro.itemquadroacesso_set.all()
        print(f"Total de itens: {itens.count()}")
        
        if itens.exists():
            # Mostrar alguns exemplos de itens
            print("  Exemplos de itens:")
            for item in itens[:3]:
                print(f"    - {item.militar.nome_completo} (Posição {item.posicao}, Pontuação: {item.pontuacao})")
        
        print()
    
    # Verificar se há militares com ficha de conceito
    militares_com_ficha = Militar.objects.filter(Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)).distinct()
    print(f"👥 Militares com ficha de conceito: {militares_com_ficha.count()}")
    
    if militares_com_ficha.exists():
        print("\n--- EXEMPLOS DE MILITARES COM FICHA ---")
        for militar in militares_com_ficha[:5]:
            ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
            print(f"  - {militar.nome_completo} ({militar.posto_graduacao}) - Pontuação: {ficha.pontos if ficha else 'N/A'}")
    
    # Verificar militares ativos
    militares_ativos = Militar.objects.filter(situacao='AT')
    print(f"\n👥 Militares ativos: {militares_ativos.count()}")
    
    if militares_ativos.exists():
        print("\n--- DISTRIBUIÇÃO POR POSTO ---")
        postos = militares_ativos.values('posto_graduacao').annotate(
            count=django.db.models.Count('id')
        ).order_by('posto_graduacao')
        
        for posto in postos:
            print(f"  - {posto['posto_graduacao']}: {posto['count']} militares")
    
    print("\n=== FIM DA VERIFICAÇÃO ===")

if __name__ == '__main__':
    verificar_quadros_existentes() 