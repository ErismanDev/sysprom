#!/usr/bin/env python
"""
Script para adicionar "BM" após o posto nas assinaturas eletrônicas e físicas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, AssinaturaQuadroAcesso, AssinaturaAta
from django.contrib.auth.models import User

def adicionar_bm_apos_posto():
    """Adiciona 'BM' após o posto nas assinaturas"""
    
    print("🔧 Modificando assinaturas para incluir 'BM' após o posto...")
    
    # Modificar assinaturas de quadro de acesso
    assinaturas_quadro = AssinaturaQuadroAcesso.objects.all()
    modificadas_quadro = 0
    
    for assinatura in assinaturas_quadro:
        if assinatura.assinado_por and hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
            militar = assinatura.assinado_por.militar
            posto_atual = militar.get_posto_graduacao_display()
            
            # Verificar se já tem "BM" no posto
            if "BM" not in posto_atual:
                # Adicionar "BM" após o posto
                posto_com_bm = f"{posto_atual} BM"
                print(f"  📝 {militar.nome_completo}: {posto_atual} → {posto_com_bm}")
                modificadas_quadro += 1
    
    # Modificar assinaturas de ata
    assinaturas_ata = AssinaturaAta.objects.all()
    modificadas_ata = 0
    
    for assinatura in assinaturas_ata:
        if assinatura.membro and assinatura.membro.militar:
            militar = assinatura.membro.militar
            posto_atual = militar.get_posto_graduacao_display()
            
            # Verificar se já tem "BM" no posto
            if "BM" not in posto_atual:
                # Adicionar "BM" após o posto
                posto_com_bm = f"{posto_atual} BM"
                print(f"  📝 {militar.nome_completo}: {posto_atual} → {posto_com_bm}")
                modificadas_ata += 1
    
    print(f"\n✅ Modificações realizadas:")
    print(f"  - Assinaturas de quadro: {modificadas_quadro}")
    print(f"  - Assinaturas de ata: {modificadas_ata}")
    print(f"  - Total: {modificadas_quadro + modificadas_ata}")

def verificar_postos_com_bm():
    """Verifica quais postos já têm 'BM'"""
    
    print("\n🔍 Verificando postos que já têm 'BM'...")
    
    militares_com_bm = []
    militares_sem_bm = []
    
    for militar in Militar.objects.all():
        posto = militar.get_posto_graduacao_display()
        if "BM" in posto:
            militares_com_bm.append((militar.nome_completo, posto))
        else:
            militares_sem_bm.append((militar.nome_completo, posto))
    
    print(f"  ✅ Militares com 'BM' no posto: {len(militares_com_bm)}")
    for nome, posto in militares_com_bm[:5]:  # Mostrar apenas os primeiros 5
        print(f"    - {nome}: {posto}")
    
    print(f"  ⚠️  Militares sem 'BM' no posto: {len(militares_sem_bm)}")
    for nome, posto in militares_sem_bm[:5]:  # Mostrar apenas os primeiros 5
        print(f"    - {nome}: {posto}")

if __name__ == "__main__":
    print("🚀 Iniciando modificação de assinaturas para incluir 'BM'...")
    
    # Verificar postos atuais
    verificar_postos_com_bm()
    
    # Executar modificações
    adicionar_bm_apos_posto()
    
    print("\n✅ Processo concluído!") 