#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso

def debug_militares_aptos():
    print("=== DEBUG: MÉTODO MILITARES_APTOS ===\n")
    
    # Pegar o quadro existente
    quadro = QuadroAcesso.objects.first()
    if not quadro:
        print("Nenhum quadro de acesso encontrado!")
        return
    
    print(f"Analisando quadro: {quadro.get_titulo_completo()}")
    print(f"Posto: {quadro.posto}")
    print(f"Quadro: {quadro.quadro}")
    print(f"Tipo: {quadro.tipo}")
    
    # 1. Buscar militares candidatos (primeira etapa do método militares_aptos)
    posto_atual = quadro.posto
    militares_candidatos = Militar.objects.filter(
        quadro=quadro.quadro,
        posto_graduacao=posto_atual,
        situacao='AT'
    )
    
    print(f"\n--- ETAPA 1: MILITARES CANDIDATOS ---")
    print(f"Militares encontrados com filtros básicos: {militares_candidatos.count()}")
    
    for militar in militares_candidatos:
        print(f"  - {militar.nome_completo} (ID: {militar.id})")
    
    # 2. Aplicar filtro de ficha de conceito (se necessário)
    if quadro.tipo == 'ANTIGUIDADE':
        print(f"\n--- ETAPA 2: QUADRO POR ANTIGUIDADE ---")
        print("Não aplicando filtro de ficha de conceito")
        militares_apos_filtro = militares_candidatos
    else:
        print(f"\n--- ETAPA 2: QUADRO POR MERECIMENTO ---")
        militares_apos_filtro = militares_candidatos.filter(
            Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
        )
        print(f"Militares após filtro de ficha de conceito: {militares_apos_filtro.count()}")
    
    # 3. Validar cada militar individualmente
    print(f"\n--- ETAPA 3: VALIDAÇÃO INDIVIDUAL ---")
    militares_aptos = []
    
    for militar in militares_apos_filtro:
        print(f"\nValidando: {militar.nome_completo}")
        
        # Validar requisitos
        apto, motivo = quadro.validar_requisitos_quadro_acesso(militar)
        print(f"  Resultado: {'Apto' if apto else 'Inapto'} - {motivo}")
        
        if apto:
            militares_aptos.append(militar)
            print(f"  ✓ Adicionado à lista de aptos")
        else:
            print(f"  ✗ Não adicionado à lista de aptos")
    
    print(f"\n--- RESULTADO FINAL ---")
    print(f"Militares aptos encontrados: {len(militares_aptos)}")
    
    # 4. Comparar com o método original
    print(f"\n--- COMPARAÇÃO COM MÉTODO ORIGINAL ---")
    militares_aptos_original = quadro.militares_aptos()
    print(f"Militares aptos pelo método original: {len(militares_aptos_original)}")
    
    # Verificar se há diferenças
    ids_manual = set(m.id for m in militares_aptos)
    ids_original = set(m.id for m in militares_aptos_original)
    
    diferencas = ids_manual.symmetric_difference(ids_original)
    if diferencas:
        print(f"Diferenças encontradas: {len(diferencas)}")
        for militar_id in diferencas:
            militar = Militar.objects.get(id=militar_id)
            if militar_id in ids_manual and militar_id not in ids_original:
                print(f"  - {militar.nome_completo}: Presente no manual, ausente no original")
            else:
                print(f"  - {militar.nome_completo}: Ausente no manual, presente no original")
    else:
        print("Nenhuma diferença encontrada entre os métodos")

if __name__ == '__main__':
    debug_militares_aptos() 