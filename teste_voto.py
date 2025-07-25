#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do formulário de voto
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import DeliberacaoComissao, VotoDeliberacao, MembroComissao
from django.contrib.auth.models import User

def testar_voto():
    """Testa o funcionamento do sistema de votos"""
    
    # Buscar uma deliberação existente
    try:
        deliberacao = DeliberacaoComissao.objects.first()
        if not deliberacao:
            print("❌ Nenhuma deliberação encontrada no sistema")
            return
        
        print(f"✅ Deliberação encontrada: {deliberacao}")
        print(f"   - Sessão: {deliberacao.sessao}")
        print(f"   - Assunto: {deliberacao.assunto}")
        print(f"   - Votos existentes: {deliberacao.votos.count()}")
        
        # Verificar membros da comissão
        membros = MembroComissao.objects.filter(comissao=deliberacao.sessao.comissao, ativo=True)
        print(f"   - Membros ativos: {membros.count()}")
        
        # Verificar presenças na sessão
        presencas = deliberacao.sessao.presencas.filter(presente=True)
        print(f"   - Membros presentes: {presencas.count()}")
        
        # Verificar votos existentes
        votos = deliberacao.votos.all()
        print(f"   - Votos registrados: {votos.count()}")
        
        for voto in votos:
            print(f"     - {voto.membro.militar.nome_completo}: {voto.get_voto_display()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar votos: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testando sistema de votos...")
    testar_voto()
    print("✅ Teste concluído!") 